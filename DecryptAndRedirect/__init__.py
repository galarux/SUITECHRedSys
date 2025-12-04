"""Azure Function HTTP trigger para manejar la notificación de RedSys."""

import base64
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional
import hmac
from urllib.parse import unquote

import azure.functions as func
from requests import HTTPError

from utils.bc_client import BusinessCentralError, call_business_central, split_bc_url
from utils.crypto import decrypt_secret
from utils.crypto import (
    compute_redsys_signature,
    decode_redsys_parameters,
)
from utils.table_storage_sdk import get_entity_by_order_code

def parse_request(req: func.HttpRequest) -> Dict[str, Any]:
    """Extrae parámetros relevantes de la petición RedSys.

    Esta implementación mínima captura:
    - El parámetro `id` de la query string.
    - El cuerpo JSON 
    - Campos clásicos de notificación (`Ds_SignatureVersion`, `Ds_MerchantParameters`, `Ds_Signature`).

    Returns:
        Diccionario con los datos recopilados para facilitar el desarrollo posterior.
    """

    payload: Dict[str, Any] = {}

    # Id opcional vía query string (?id=...)
    if "id" in req.params:
        payload["id"] = req.params.get("id")

    # Intentar leer JSON
    try:
        body_json = req.get_json()
        if isinstance(body_json, dict):
            payload.update(body_json)
    except ValueError:
        # Puede llegar como form-urlencoded; lo dejaremos para una iteración posterior.
        logging.debug("Cuerpo no es JSON válido; se procesará más adelante.")

    # Compatibilidad con form-urlencoded: azure functions expone req.form
    try:
        form_data = req.form
        for key in ("Ds_SignatureVersion", "Ds_MerchantParameters", "Ds_Signature"):
            if key in form_data:
                payload[key] = form_data[key]
    except AttributeError:
        # No hay soporte form-data en tipos anteriores o está vacío.
        pass

    return payload


def parse_amount(amount_value: str | None) -> float | None:
    if not amount_value:
        return None
    try:
        return float(Decimal(amount_value) / Decimal("100"))
    except Exception:  # pylint: disable=broad-except
        logging.warning("No se pudo convertir Ds_Amount='%s'", amount_value)
        return None


def parse_datetime(date_value: str | None, hour_value: str | None) -> str | None:
    if not date_value or not hour_value:
        return None
    try:
        dt = datetime.strptime(f"{date_value} {hour_value}", "%d/%m/%Y %H:%M")
        return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        logging.warning("No se pudo convertir fecha/hora '%s' '%s'", date_value, hour_value)
        return None


def build_bc_payload(decoded_params: Dict[str, Any], signature: str, order: str) -> Dict[str, Any]:
    """Construye el payload que espera BC: `order` y `paymentInfo` como string JSON.

    El formato esperado:
    {
        "order": "...",
        "paymentInfo": "{\"order\":\"...\",\"merchantCode\":\"...\", ... }"
    }
    """

    # Formatear fecha/hora como en el ejemplo: "dd/MM/yyyy HH:mm"
    notification_dt: str | None = None
    if decoded_params.get("Ds_Date") and decoded_params.get("Ds_Hour"):
        notification_dt = f"{decoded_params['Ds_Date']} {decoded_params['Ds_Hour']}"

    payment_info: Dict[str, Any] = {
        "order": order,
        "merchantCode": decoded_params.get("Ds_MerchantCode"),
        "terminal": decoded_params.get("Ds_Terminal"),
        "amount": decoded_params.get("Ds_Amount"),
        "currency": decoded_params.get("Ds_Currency"),
        "transactionType": decoded_params.get("Ds_TransactionType"),
        "responseCode": decoded_params.get("Ds_Response"),
        "authorizationCode": decoded_params.get("Ds_AuthorisationCode"),
        "securePayment": decoded_params.get("Ds_SecurePayment"),
        "cardNumber": decoded_params.get("Ds_Card_Number"),
        "cardCountry": decoded_params.get("Ds_Card_Country"),
        "cardBrand": decoded_params.get("Ds_Card_Brand"),
        "cardTypology": decoded_params.get("Ds_Card_Typology"),
        "processedPayMethod": decoded_params.get("Ds_ProcessedPayMethod"),
        "consumerLanguage": decoded_params.get("Ds_ConsumerLanguage"),
        "merchantData": decoded_params.get("Ds_MerchantData"),
        "notificationDateTime": notification_dt,
        "titular": decoded_params.get("Ds_Titular"),
        "signature": signature or "",
    }

    # Quitar los None para que el JSON sea limpio
    filtered_payment_info = {k: v for k, v in payment_info.items() if v is not None}

    return {
        "order": order,  # La API de BC espera "order", no "merchantOrder"
        "paymentInfo": json.dumps(filtered_payment_info, ensure_ascii=False)
    }


def escape_odata_key(value: str) -> str:
    return value.replace("'", "''")


def upload_stream_property(
    entity: Dict[str, Any],
    relative_resource: Optional[str],
    order: str,
    stream_name: str,
    content: str,
    content_type: str,
) -> None:
    if not relative_resource:
        return
    escaped_order = escape_odata_key(order)
    normalized_resource = relative_resource.strip("/")
    if not normalized_resource:
        return
    stream_path = f"{normalized_resource}" f"('{escaped_order}')/{stream_name}/$value"
    call_business_central(
        entity,
        method="PUT",
        relative_path=stream_path,
        payload=content,
        headers={"Content-Type": content_type},
    )


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("DecryptAndRedirect recibido: procesando notificación RedSys")

    data = parse_request(req)

    ds_params_b64 = data.get("Ds_MerchantParameters")
    ds_signature = data.get("Ds_Signature")

    if not ds_params_b64 or not ds_signature:
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "Faltan Ds_MerchantParameters o Ds_Signature",
                    "received": data,
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=400,
        )

    terminal_key = os.environ.get("REDSYS_SHA256_KEY")
    if not terminal_key:
        logging.error("Variable de entorno REDSYS_SHA256_KEY no configurada")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "Configuración incompleta en servidor",
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=500,
        )

    try:
        decoded_params_raw = decode_redsys_parameters(ds_params_b64)
        decoded_params = {
            key: unquote(value) if isinstance(value, str) else value
            for key, value in decoded_params_raw.items()
        }
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("No se pudo decodificar Ds_MerchantParameters")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "Ds_MerchantParameters inválido",
                    "detail": str(exc),
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=400,
        )

    ds_order = decoded_params.get("Ds_Order")
    if not ds_order:
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "No se encontró Ds_Order en Ds_MerchantParameters",
                    "decoded": decoded_params,
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=400,
        )

    entity = get_entity_by_order_code(ds_order)
    if not entity:
        logging.warning("No se encontró entidad asociada a Ds_Merchant_Order", extra={"Ds_Order": ds_order})
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "Id no registrado",
                    "decoded": decoded_params,
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=404,
        )

    expected_signature = compute_redsys_signature(
        merchant_parameters_b64=ds_params_b64,
        order=ds_order,
        terminal_key_b64=terminal_key,
    )

    normalized_signature = ds_signature.replace("-", "+").replace("_", "/")
    padding = len(normalized_signature) % 4
    if padding:
        normalized_signature += "=" * (4 - padding)

    try:
        expected_bytes = base64.b64decode(expected_signature)
        received_bytes = base64.b64decode(normalized_signature)
        signature_valid = hmac.compare_digest(expected_bytes, received_bytes)
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("Error al normalizar firmas RedSys")
        signature_valid = False

    bc_call_summary: Dict[str, Any] | None = None
    if signature_valid:
        bc_payload = build_bc_payload(decoded_params, ds_signature, ds_order)
        endpoint_url = entity.get("URLBC", "")
        base_url, relative_path = split_bc_url(endpoint_url)
        legacy_path = entity.get("BCPath")
        if not relative_path and legacy_path:
            relative_path = legacy_path
        bc_path = relative_path or legacy_path or ""
        call_entity = dict(entity)
        call_entity["URLBC"] = base_url or endpoint_url
        bc_method = (entity.get("BCMethod") or "POST").upper()
        if call_entity.get("PassEncrypted") and call_entity.get("Pass") and call_entity.get("EncryptKey"):
            try:
                call_entity["Pass"] = decrypt_secret(call_entity["Pass"], call_entity["EncryptKey"])
            except Exception as exc:
                logging.exception("No se pudo descifrar las credenciales de Business Central")
                return func.HttpResponse(
                    json.dumps(
                        {
                            "error": "No se pudieron descifrar las credenciales de Business Central",
                            "detail": str(exc),
                        },
                        ensure_ascii=False,
                    ),
                    mimetype="application/json",
                    status_code=500,
                )
        final_url = endpoint_url
        if relative_path and (base_url or endpoint_url):
            base_for_summary = base_url or endpoint_url
            final_url = f"{base_for_summary.rstrip('/')}/{relative_path.lstrip('/')}"

        # Log del payload que se va a enviar a BC
        payload_str = json.dumps(bc_payload, ensure_ascii=False, indent=2)
        logging.info("ENVIANDO A BC - URL: %s, Método: %s", final_url, bc_method)
        logging.info("PAYLOAD ENVIADO A BC: %s", payload_str)

        try:
            bc_response = call_business_central(
                call_entity,
                method=bc_method,
                relative_path=relative_path,
                payload=bc_payload,
            )
            logging.info("Business Central respondió con status: %s", bc_response.status_code)
            bc_status = bc_response.status_code
            try:
                bc_content = bc_response.json()
            except ValueError:
                bc_content = {"raw": bc_response.text}

            bc_call_summary = {
                "status": bc_status,
                "method": bc_method,
                "url": final_url,
                "payload": bc_content,
                "sentPayload": bc_payload,  # Temporal: para verificar el formato de paymentInfo
            }
            bc_response.raise_for_status()

            if bc_method == "POST" and bc_status < 400:
                try:
                    upload_stream_property(
                        call_entity,
                        relative_path,
                        ds_order,
                        "jsonPayload",
                        json.dumps(decoded_params, ensure_ascii=False),
                        "application/json; charset=utf-8",
                    )
                except Exception:  # pylint: disable=broad-except
                    logging.exception("No se pudo subir jsonPayload a Business Central")
                try:
                    upload_stream_property(
                        call_entity,
                        relative_path,
                        ds_order,
                        "rawParameters",
                        ds_params_b64,
                        "text/plain; charset=utf-8",
                    )
                except Exception:  # pylint: disable=broad-except
                    logging.exception("No se pudo subir rawParameters a Business Central")
        except HTTPError as http_error:
            status_code = http_error.response.status_code if http_error.response else 502
            body = http_error.response.text if http_error.response else str(http_error)
            
            # Capturar más detalles del error
            error_details = {"raw": body}
            if http_error.response:
                try:
                    error_json = http_error.response.json()
                    error_details = error_json
                    logging.error("ERROR BC JSON: %s", json.dumps(error_json, ensure_ascii=False, indent=2))
                except (ValueError, AttributeError):
                    error_details = {"raw": body, "text": body[:1000]}  # Limitar tamaño
                    logging.error("ERROR BC TEXT: %s", body[:1000])
                
                # Capturar headers relevantes
                error_details["responseHeaders"] = dict(http_error.response.headers)
            
            payload_str = json.dumps(bc_payload, ensure_ascii=False, indent=2)
            logging.error("ERROR BC - Status: %s, URL: %s", status_code, final_url)
            logging.error("PAYLOAD QUE SE ENVIÓ: %s", payload_str)
            logging.error("RESPUESTA COMPLETA BC: %s", json.dumps(error_details, ensure_ascii=False, indent=2))
            
            bc_call_summary = {
                "status": status_code,
                "method": bc_method,
                "url": final_url,
                "path": bc_path,
                "error": body[:1000] if len(body) > 1000 else body,  # Limitar tamaño
                "errorDetails": error_details,
                "sentPayload": bc_payload,  # Incluir payload enviado para debugging
            }
        except BusinessCentralError as bc_error:
            logging.error("Error de configuración para Business Central: %s", bc_error)
            bc_call_summary = {
                "status": 400,
                "method": bc_method,
                "url": final_url,
                "path": bc_path,
                "error": str(bc_error),
                "sentPayload": bc_payload,  # Incluir payload enviado para debugging
            }
        except Exception as exc:  # pylint: disable=broad-except
            logging.exception("Error llamando a Business Central desde DecryptAndRedirect")
            bc_call_summary = {
                "status": 500,
                "method": bc_method,
                "url": final_url,
                "path": bc_path,
                "error": str(exc),
                "sentPayload": bc_payload,  # Incluir payload enviado para debugging
            }

    response: Dict[str, Any] = {
        "message": "Notificación procesada",
        "received": data,
        "decodedParameters": decoded_params,
        "signatureValid": signature_valid,
        "bcCall": bc_call_summary,
        "expectedSignature": expected_signature if not signature_valid else None,
    }

    try:
        logging.info(json.dumps(response, ensure_ascii=False))
        status_code = 200 if signature_valid else 401
        if signature_valid and bc_call_summary and bc_call_summary.get("status", 200) >= 400:
            status_code = bc_call_summary["status"]
        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=status_code,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("Error enviando respuesta DecryptAndRedirect")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": str(exc),
                    "received": data,
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=500,
        )
