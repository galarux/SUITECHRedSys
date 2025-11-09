import json
import logging
from typing import Optional

import azure.functions as func
from requests import HTTPError

from utils.bc_client import BusinessCentralError, call_business_central
from utils.table_storage_sdk import get_entity_by_order_code

DEFAULT_METHOD = "GET"


def _get_request_value(req: func.HttpRequest, key: str) -> Optional[str]:
    if key in req.params:
        return req.params.get(key)
    try:
        body = req.get_json()
        return body.get(key)
    except (ValueError, AttributeError):
        return None


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("BCCompanies invocado.")

    order_code = _get_request_value(req, "order")
    if not order_code:
        return func.HttpResponse(
            json.dumps({"error": "Parámetro 'order' requerido."}),
            mimetype="application/json",
            status_code=400,
        )

    entity = get_entity_by_order_code(order_code)
    if not entity:
        return func.HttpResponse(
            json.dumps({"error": f"No se encontró configuración para order {order_code}."}),
            mimetype="application/json",
            status_code=404,
        )

    method = (_get_request_value(req, "method") or entity.get("BCMethod") or DEFAULT_METHOD).upper()
    relative_path = _get_request_value(req, "path") or entity.get("BCPath")
    payload = None

    try:
        payload = req.get_json()
    except ValueError:
        payload = None

    # Evitar que order/method/path se envíen al backend si vienen en JSON de control
    if isinstance(payload, dict):
        payload.pop("order", None)
        payload.pop("method", None)
        payload.pop("path", None)
    else:
        payload = None

    try:
        response = call_business_central(
            entity,
            method=method,
            relative_path=relative_path,
            payload=payload,
        )
        response.raise_for_status()
    except HTTPError as http_error:
        status = http_error.response.status_code if http_error.response else 502
        body = http_error.response.text if http_error.response else str(http_error)
        logging.error("Error HTTP Business Central: %s %s", status, body)
        return func.HttpResponse(
            json.dumps({"error": "Business Central devolvió error", "status": status, "body": body}),
            mimetype="application/json",
            status_code=status,
        )
    except BusinessCentralError as bc_error:
        logging.error("Error de configuración Business Central: %s", bc_error)
        return func.HttpResponse(
            json.dumps({"error": str(bc_error)}),
            mimetype="application/json",
            status_code=400,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("Error llamando a Business Central")
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            mimetype="application/json",
            status_code=500,
        )

    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}

    return func.HttpResponse(
        json.dumps(
            {
                "order": order_code,
                "authType": entity.get("AuthType"),
                "method": method,
                "path": relative_path,
                "result": payload,
            }
        ),
        mimetype="application/json",
        status_code=200,
    )

