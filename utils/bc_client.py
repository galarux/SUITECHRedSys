import json
from typing import Any, Dict, Optional, Tuple, Union
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


def split_bc_url(url_bc: str) -> Tuple[str, Optional[str]]:
    """Divide una URL completa de BC en base y ruta relativa."""
    if not url_bc:
        return "", None

    parsed = urlparse(url_bc)
    segments = [segment for segment in parsed.path.split("/") if segment]
    if not segments:
        return url_bc, None

    base_segment_count = 0
    if segments[0].lower() == "v2.0" and len(segments) >= 3:
        base_segment_count = 3
    elif segments[0].lower().startswith("bc"):
        base_segment_count = 1

    if base_segment_count:
        base_path = "/" + "/".join(segments[:base_segment_count])
        relative_segments = segments[base_segment_count:]
        relative_path = "/".join(relative_segments) if relative_segments else None
        base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
        return base_url, relative_path

    return url_bc, None


PayloadType = Optional[Union[Dict[str, Any], list, str, bytes]]


def _prepare_request_components(
    payload: PayloadType,
    headers: Optional[Dict[str, str]],
) -> Tuple[Optional[Dict[str, str]], Optional[Union[str, bytes]]]:
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)

    if payload is None:
        return request_headers, None

    if isinstance(payload, (dict, list)):
        request_headers.setdefault("Content-Type", "application/json")
        return request_headers, json.dumps(payload)

    if isinstance(payload, (str, bytes)):
        # Permitir que quien llama defina Content-Type; si no, asumir texto plano
        request_headers.setdefault("Content-Type", "text/plain; charset=utf-8")
        return request_headers, payload

    raise BusinessCentralError(f"Tipo de payload no soportado: {type(payload)!r}")


def _request_oauth(
    entity: Dict[str, Any],
    method: str,
    url: str,
    payload: PayloadType,
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

    auth_headers = {"Authorization": f"Bearer {access_token}"}
    request_headers, data = _prepare_request_components(payload, headers)
    if request_headers:
        auth_headers.update(request_headers)
    return requests.request(method, url, headers=auth_headers, data=data, timeout=30)


def _request_basic(
    entity: Dict[str, Any],
    method: str,
    url: str,
    payload: PayloadType,
    headers: Optional[Dict[str, str]],
) -> requests.Response:
    user = entity.get("User")
    password = entity.get("Pass")

    if not user or not password:
        raise BusinessCentralError("Entidad BC incompleta para Basic Auth (User/Pass requeridos).")

    request_headers, data = _prepare_request_components(payload, headers)
    return requests.request(
        method,
        url,
        headers=request_headers,
        data=data,
        auth=(user, password),
        timeout=30,
    )


def call_business_central(
    entity: Dict[str, Any],
    method: str = "GET",
    relative_path: Optional[str] = None,
    payload: PayloadType = None,
    headers: Optional[Dict[str, str]] = None,
) -> requests.Response:
    """Realiza la llamada a Business Central usando la configuración almacenada."""
    if "URLBC" not in entity:
        raise BusinessCentralError("Entidad sin URLBC definida.")

    method = method.upper()
    if method not in SUPPORTED_METHODS:
        raise BusinessCentralError(f"Método HTTP '{method}' no soportado.")

    auth_type = (entity.get("AuthType") or "").lower()
    if auth_type == "oauth":
        _, _, base_url = parse_bc_url(entity["URLBC"])
        url = entity["URLBC"]
        if relative_path:
            url = f"{base_url}/{relative_path.lstrip('/')}"
        return _request_oauth(entity, method, url, payload, headers)
    if auth_type == "basic":
        url = _build_basic_url(entity["URLBC"], relative_path)
        return _request_basic(entity, method, url, payload, headers)

    raise BusinessCentralError(f"AuthType '{auth_type}' no soportado.")


def _build_basic_url(base_url: str, relative_path: Optional[str]) -> str:
    if not base_url:
        raise BusinessCentralError("Entidad sin URLBC definida.")

    base = base_url.rstrip("/")
    if not relative_path:
        return base

    if relative_path.lower().startswith(("http://", "https://")):
        return relative_path

    normalized_base = base.lower()
    normalized_path = relative_path.lstrip("/").lower()
    if normalized_base.endswith(normalized_path):
        return base

    return f"{base}/{relative_path.lstrip('/')}"

