import json
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import requests

DEFAULT_SCOPE = "https://api.businesscentral.dynamics.com/.default"
TOKEN_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
SUPPORTED_METHODS = {"GET", "POST", "PATCH", "PUT", "DELETE"}


class BusinessCentralError(Exception):
    """Error genérico para llamadas a Business Central."""


def parse_bc_url(url_bc: str) -> Tuple[str, str, str]:
    """Devuelve (tenant, environment, base_url) a partir de la URL de BC."""
    parsed = urlparse(url_bc)
    segments = [segment for segment in parsed.path.split("/") if segment]

    if len(segments) < 3 or segments[0].lower() != "v2.0":
        raise BusinessCentralError("URL de Business Central no sigue el formato esperado.")

    tenant = segments[1]
    environment = segments[2]
    base = f"{parsed.scheme}://{parsed.netloc}/v2.0/{tenant}/{environment}"
    return tenant, environment, base


def _request_oauth(
    entity: Dict[str, Any],
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]],
    headers: Optional[Dict[str, str]],
) -> requests.Response:
    client_id = entity.get("User")
    client_secret = entity.get("Pass")

    if not client_id or not client_secret:
        raise BusinessCentralError("Entidad BC incompleta para OAuth (User/Pass requeridos).")

    tenant, _, _ = parse_bc_url(entity["URLBC"])

    token_payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": DEFAULT_SCOPE,
    }

    token_url = TOKEN_URL_TEMPLATE.format(tenant=tenant)
    token_response = requests.post(token_url, data=token_payload, timeout=30)
    token_response.raise_for_status()

    access_token = token_response.json().get("access_token")
    if not access_token:
        raise BusinessCentralError("Respuesta de token inválida (sin access_token).")

    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    if payload is not None:
        auth_headers["Content-Type"] = "application/json"

    if headers:
        auth_headers.update(headers)

    data = json.dumps(payload) if payload is not None else None
    return requests.request(method, url, headers=auth_headers, data=data, timeout=30)


def _request_basic(
    entity: Dict[str, Any],
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]],
    headers: Optional[Dict[str, str]],
) -> requests.Response:
    user = entity.get("User")
    password = entity.get("Pass")

    if not user or not password:
        raise BusinessCentralError("Entidad BC incompleta para Basic Auth (User/Pass requeridos).")

    request_headers = {"Accept": "application/json"}
    if payload is not None:
        request_headers["Content-Type"] = "application/json"

    if headers:
        request_headers.update(headers)

    data = json.dumps(payload) if payload is not None else None
    return requests.request(method, url, headers=request_headers, data=data, auth=(user, password), timeout=30)


def call_business_central(
    entity: Dict[str, Any],
    method: str = "GET",
    relative_path: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> requests.Response:
    """Realiza la llamada a Business Central usando la configuración almacenada."""
    if "URLBC" not in entity:
        raise BusinessCentralError("Entidad sin URLBC definida.")

    method = method.upper()
    if method not in SUPPORTED_METHODS:
        raise BusinessCentralError(f"Método HTTP '{method}' no soportado.")

    _, _, base_url = parse_bc_url(entity["URLBC"])
    url = entity["URLBC"]
    if relative_path:
        url = f"{base_url}/{relative_path.lstrip('/')}"

    auth_type = (entity.get("AuthType") or "").lower()
    if auth_type == "oauth":
        return _request_oauth(entity, method, url, payload, headers)
    if auth_type == "basic":
        return _request_basic(entity, method, url, payload, headers)

    raise BusinessCentralError(f"AuthType '{auth_type}' no soportado.")

