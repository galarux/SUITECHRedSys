import base64
import json
import logging
import os
from typing import Any, Dict, Optional

import azure.functions as func
import requests

from utils.crypto import compute_paygold_signature
from utils.table_storage_sdk import save_to_table

DEFAULT_REST_TEST_URL = "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST"


def _load_body(req: func.HttpRequest) -> Dict[str, Any]:
    try:
        return req.get_json()
    except ValueError as exc:
        raise ValueError("El cuerpo debe ser un JSON válido") from exc


def _normalize_encrypt_data(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("El campo 'encryptData' debe ser un JSON válido") from exc
        if not isinstance(parsed, dict):
            raise ValueError("El campo 'encryptData' debe representar un objeto JSON")
        return parsed
    raise ValueError("El campo 'encryptData' debe ser un objeto o cadena JSON")


def _collect_seed_parameters(payload: Dict[str, Any], encrypt_data: Dict[str, Any]) -> Dict[str, Any]:
    seed: Dict[str, Any] = {}

    custom_parameters = payload.get("merchantParameters") or payload.get("merchant_parameters")
    if isinstance(custom_parameters, dict):
        seed.update(custom_parameters)

    for key, value in encrypt_data.items():
        if key and value is not None:
            normalized_key = key.upper() if key.upper().startswith("DS_") else key
            seed.setdefault(normalized_key, value)

    for key, value in payload.items():
        if isinstance(key, str) and key.upper().startswith("DS_") and value is not None:
            seed.setdefault(key.upper(), value)

    return seed


def _resolve_config(payload: Dict[str, Any], merchant_parameters: Dict[str, Any]) -> Dict[str, str]:
    merchant_code = (
        payload.get("merchantCode")
        or merchant_parameters.get("DS_MERCHANT_MERCHANTCODE")
        or os.environ.get("REDSYS_MERCHANT_CODE")
    )
    terminal = (
        payload.get("terminal")
        or merchant_parameters.get("DS_MERCHANT_TERMINAL")
        or os.environ.get("REDSYS_TERMINAL")
    )
    currency = (
        payload.get("currency")
        or merchant_parameters.get("DS_MERCHANT_CURRENCY")
        or os.environ.get("REDSYS_CURRENCY")
        or os.environ.get("PAYGOLD_CURRENCY")
        or "978"
    )
    secret_key = (
        payload.get("encryptKey")
        or payload.get("secretKey")
        or os.environ.get("PAYGOLD_SHA256_KEY")
        or os.environ.get("REDSYS_SHA256_KEY")
    )
    rest_url = (
        payload.get("redirectURL")
        or payload.get("restUrl")
        or os.environ.get("PAYGOLD_REST_URL")
        or os.environ.get("REDSYS_REST_URL")
        or DEFAULT_REST_TEST_URL
    )

    missing = [name for name, value in [
        ("merchantCode", merchant_code),
        ("terminal", terminal),
        ("secretKey", secret_key),
        ("restUrl", rest_url),
    ] if not value]

    if missing:
        raise ValueError(f"Faltan parámetros obligatorios: {', '.join(missing)}")

    return {
        "merchantCode": str(merchant_code),
        "terminal": str(terminal),
        "currency": str(currency),
        "secretKey": str(secret_key),
        "restUrl": str(rest_url),
    }


def _coerce_parameter_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _build_merchant_parameters(
    payload: Dict[str, Any],
    config: Dict[str, str],
) -> Dict[str, str]:
    merchant_parameters: Dict[str, str] = {}

    custom_parameters = payload.get("merchantParameters") or payload.get("merchant_parameters")
    if isinstance(custom_parameters, dict):
        for key, value in custom_parameters.items():
            if key and value is not None:
                merchant_parameters[str(key)] = _coerce_parameter_value(value)

    if not merchant_parameters:
        for key, value in payload.items():
            if isinstance(key, str) and key.upper().startswith("DS_") and value is not None:
                merchant_parameters[key.upper()] = _coerce_parameter_value(value)

    def ensure(field: str, value: Optional[str]) -> None:
        if value is not None and field not in merchant_parameters:
            merchant_parameters[field] = value

    amount = payload.get("amount")
    order = payload.get("order")
    transaction_type = payload.get("transactionType")

    ensure("DS_MERCHANT_AMOUNT", str(amount) if amount is not None else None)
    ensure("DS_MERCHANT_ORDER", str(order) if order is not None else None)
    ensure("DS_MERCHANT_TRANSACTIONTYPE", str(transaction_type) if transaction_type is not None else None)

    ensure("DS_MERCHANT_MERCHANTCODE", config["merchantCode"])
    ensure("DS_MERCHANT_TERMINAL", config["terminal"])
    ensure("DS_MERCHANT_CURRENCY", config["currency"])

    if payload.get("productDescription"):
        ensure("DS_MERCHANT_PRODUCTDESCRIPTION", str(payload["productDescription"]))
    if payload.get("titular"):
        ensure("DS_MERCHANT_TITULAR", str(payload["titular"]))
    if payload.get("payMethods"):
        ensure("DS_MERCHANT_PAYMETHODS", str(payload["payMethods"]))
    if payload.get("merchantData"):
        ensure("DS_MERCHANT_MERCHANTDATA", str(payload["merchantData"]))
    if payload.get("notifyUrl"):
        ensure("DS_MERCHANT_NOTIFY_URL", str(payload["notifyUrl"]))
    if payload.get("buyerRegistration"):
        ensure("DS_MERCHANT_BUYERREGISTRATION", str(payload["buyerRegistration"]))
    if payload.get("consumerLanguage"):
        ensure("DS_MERCHANT_CONSUMERLANGUAGE", str(payload["consumerLanguage"]))
    if payload.get("identifier"):
        ensure("DS_MERCHANT_IDENTIFIER", str(payload["identifier"]))
    if payload.get("expiryDate"):
        ensure("DS_MERCHANT_EXPIRYDATE", str(payload["expiryDate"]))

    extra_parameters = payload.get("extraParameters")
    if isinstance(extra_parameters, dict):
        for key, value in extra_parameters.items():
            if value is not None:
                merchant_parameters[str(key)] = _coerce_parameter_value(value)

    paygold_flag = payload.get("paygold")
    if paygold_flag is not None:
        if str(paygold_flag).lower() in ("true", "1", "yes", "si"):
            merchant_parameters.setdefault("DS_MERCHANT_PAYGOLD", "true")
    elif payload.get("DS_MERCHANT_PAYGOLD") is True:
        merchant_parameters.setdefault("DS_MERCHANT_PAYGOLD", "true")

    if "DS_MERCHANT_TRANSACTIONTYPE" not in merchant_parameters:
        merchant_parameters["DS_MERCHANT_TRANSACTIONTYPE"] = "0"

    required_missing = [
        field for field in ("DS_MERCHANT_AMOUNT", "DS_MERCHANT_ORDER")
        if field not in merchant_parameters or merchant_parameters[field] in ("", None)
    ]
    if required_missing:
        missing_display = ", ".join(required_missing)
        raise ValueError(f"Faltan campos obligatorios en los parámetros: {missing_display}")

    return merchant_parameters


def _encode_parameters(merchant_parameters: Dict[str, str]) -> str:
    serialized = json.dumps(merchant_parameters, separators=(",", ":"), ensure_ascii=False)
    return base64.b64encode(serialized.encode("utf-8")).decode("utf-8")


def _build_request_payload(
    merchant_parameters: Dict[str, str],
    merchant_parameters_b64: str,
    secret_key_b64: str,
) -> Dict[str, str]:
    order = merchant_parameters.get("DS_MERCHANT_ORDER")
    if not order:
        raise ValueError("Missing field 'DS_MERCHANT_ORDER' para firmar la petición.")
    signature = compute_paygold_signature(merchant_parameters_b64, order, secret_key_b64)
    return {
        "Ds_MerchantParameters": merchant_parameters_b64,
        "Ds_SignatureVersion": "HMAC_SHA256_V1",
        "Ds_Signature": signature,
    }


def _send_request(rest_url: str, payload: Dict[str, str], timeout: Optional[float]) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    response = requests.post(rest_url, headers=headers, json=payload, timeout=timeout or 30)
    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("PaygoldLink: procesando solicitud para generar Paygold")

    body: Dict[str, Any] = {}
    merchant_parameters_seed: Dict[str, Any] = {}
    merchant_parameters: Dict[str, str] = {}
    config: Dict[str, str] = {}
    entity_id: Optional[str] = None

    try:
        body = _load_body(req)
        encrypt_data = _normalize_encrypt_data(body.get("encryptData"))
        merchant_parameters_seed = _collect_seed_parameters(body, encrypt_data)

        parameter_payload = dict(body)
        if merchant_parameters_seed:
            parameter_payload["merchantParameters"] = merchant_parameters_seed
        elif encrypt_data:
            parameter_payload["merchantParameters"] = encrypt_data

        config = _resolve_config(body, parameter_payload.get("merchantParameters") or {})
        merchant_parameters = _build_merchant_parameters(parameter_payload, config)

        url_bc = body.get("urlBC")
        auth_type = body.get("authType")
        user = body.get("user")
        password = body.get("pass")
        encrypt_type = body.get("encryptType", "SHA-256")
        redirect_url = config["restUrl"]

        if not url_bc:
            raise ValueError("Missing field 'urlBC'")
        if not auth_type:
            raise ValueError("Missing field 'authType'")
        if auth_type not in ("Basic", "oAuth"):
            raise ValueError("Invalid 'authType'. Debe ser 'Basic' u 'oAuth'")
        if not user:
            raise ValueError("Missing field 'user'")
        if not password:
            raise ValueError("Missing field 'pass'")

        merchant_parameters_b64 = _encode_parameters(merchant_parameters)
        request_payload = _build_request_payload(merchant_parameters, merchant_parameters_b64, config["secretKey"])

        ds_order = merchant_parameters.get("DS_MERCHANT_ORDER")

        entity_id = save_to_table(
            url_bc=url_bc,
            auth_type=auth_type,
            user=user,
            password=password,
            encrypt_type=encrypt_type,
            encrypt_key=config["secretKey"],
            ds_merchant_order=ds_order,
            redirect_url=redirect_url,
        )
        if not entity_id:
            raise RuntimeError("No se pudo persistir la configuración en Table Storage")

        logging.info(
            "PaygoldLink debug: %s",
            json.dumps(
                {
                    "order": ds_order,
                    "entityId": entity_id,
                    "restUrl": redirect_url,
                    "merchantParameters": merchant_parameters,
                    "merchantParametersB64": merchant_parameters_b64,
                    "signature": request_payload["Ds_Signature"],
                },
                ensure_ascii=False,
            ),
        )

        timeout_value = body.get("timeout")
        timeout_seconds: Optional[float] = None
        if isinstance(timeout_value, (int, float)):
            timeout_seconds = float(timeout_value)

        rest_response = _send_request(redirect_url, request_payload, timeout_seconds)

        result = {
            "message": "Paygold generado correctamente",
            "entityId": entity_id,
            "request": {
                "restUrl": redirect_url,
                "merchantParameters": merchant_parameters,
                "merchantParametersB64": merchant_parameters_b64,
            },
            "response": rest_response,
        }

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200,
        )
    except requests.HTTPError as http_error:
        status_code = http_error.response.status_code if http_error.response else 502
        content = http_error.response.text if http_error.response else str(http_error)
        logging.exception("Error HTTP al llamar a Paygold")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "La API de RedSys devolvió un error",
                    "detail": content,
                    "status": status_code,
                    "entityId": entity_id,
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=status_code,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("Error generando Paygold")
        try:
            if not entity_id and body:
                url_bc = body.get("urlBC")
                auth_type = body.get("authType")
                user = body.get("user")
                password = body.get("pass")
                encrypt_type = body.get("encryptType", "SHA-256")
                encrypt_key = (
                    (config or {}).get("secretKey")
                    or body.get("encryptKey")
                    or os.environ.get("PAYGOLD_SHA256_KEY")
                    or os.environ.get("REDSYS_SHA256_KEY")
                )
                if url_bc and auth_type and user and password and encrypt_key:
                    save_to_table(
                        url_bc=url_bc,
                        auth_type=auth_type,
                        user=user,
                        password=password,
                        encrypt_type=encrypt_type,
                        encrypt_key=encrypt_key,
                        ds_merchant_order=(merchant_parameters or {}).get("DS_MERCHANT_ORDER")
                        or merchant_parameters_seed.get("DS_MERCHANT_ORDER"),
                        redirect_url=(config or {}).get("restUrl"),
                        error=str(exc),
                    )
        except Exception:  # pylint: disable=broad-except
            logging.exception("No se pudo registrar el error en Table Storage")

        return func.HttpResponse(
            json.dumps(
                {
                    "error": str(exc),
                    "entityId": entity_id,
                },
                ensure_ascii=False,
            ),
            mimetype="application/json",
            status_code=400,
        )

