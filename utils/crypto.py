import base64
import hashlib
import hmac
import json
from typing import Any, Dict

from Crypto.Cipher import DES3, AES
from Crypto.Random import get_random_bytes


def encrypt(data: str, key: str, encrypt_type: str) -> str:
    message = (data + key).encode("utf-8")
    if encrypt_type.upper() == "SHA-512":
        return hashlib.sha512(message).hexdigest()
    return hashlib.sha256(message).hexdigest()


def _derive_aes_key(encrypt_key: str) -> bytes:
    if not encrypt_key:
        raise ValueError("Clave de cifrado vacía.")
    try:
        material = base64.b64decode(encrypt_key)
    except Exception:
        material = encrypt_key.encode("utf-8")
    return hashlib.sha256(material).digest()


def encrypt_secret(secret: str, encrypt_key: str) -> str:
    if secret is None:
        raise ValueError("No se puede cifrar un valor nulo.")
    key = _derive_aes_key(encrypt_key)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(secret.encode("utf-8"))
    payload = nonce + tag + ciphertext
    return base64.b64encode(payload).decode("utf-8")


def decrypt_secret(token: str, encrypt_key: str) -> str:
    if token is None:
        raise ValueError("Token vacío.")
    raw = base64.b64decode(token)
    if len(raw) < 28:
        raise ValueError("Token de cifrado inválido.")
    nonce = raw[:12]
    tag = raw[12:28]
    ciphertext = raw[28:]
    key = _derive_aes_key(encrypt_key)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode("utf-8")


def _prepare_3des_key(raw_key: bytes) -> bytes:
    """Ajusta la clave proporcionada por RedSys para cifrado 3DES.

    RedSys entrega la clave SHA-256 codificada en Base64. Una vez decodificada
    debe tener una longitud de 24 bytes para DESede. Si es más corta, se rellena
    repitiendo y truncando según especificación.
    """

    if len(raw_key) < 24:
        raw_key = (raw_key * (24 // len(raw_key) + 1))[:24]
    return raw_key


def diversify_redsys_key(order: str, terminal_key_b64: str) -> bytes:
    """Genera la clave diversificada para firmar/validar notificaciones.

    Args:
        order: Ds_Order de la operación.
        terminal_key_b64: clave SHA-256 del TPV codificada en Base64.

    Returns:
        Clave diversificada (bytes) resultante del cifrado 3DES en modo CBC con
        IV=0 sobre `order`, tal como indica RedSys.
    """

    base_key = base64.b64decode(terminal_key_b64)
    key_bytes = _prepare_3des_key(base_key)
    cipher = DES3.new(key_bytes, DES3.MODE_CBC, iv=b"\x00" * 8)

    # El mensaje debe ser múltiplo de 8 bytes. RedSys indica paddings con \0.
    message = order.encode("utf-8")
    pad_len = (8 - len(message) % 8) % 8
    message += b"\x00" * pad_len

    diversified = cipher.encrypt(message)
    return diversified


def compute_redsys_signature(merchant_parameters_b64: str, order: str, terminal_key_b64: str) -> str:
    """Calcula la firma HMAC-SHA256 según documentación de RedSys.

    Args:
        merchant_parameters_b64: valor enviado en Ds_MerchantParameters (Base64).
        order: Ds_Order recuperado al decodificar los parámetros.
        terminal_key_b64: clave del TPV (Base64) de Azure Settings.

    Returns:
        Firma codificada en Base64 lista para comparar con Ds_Signature.
    """

    diversified_key = diversify_redsys_key(order, terminal_key_b64)
    digest = hmac.new(
        diversified_key,
        merchant_parameters_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def decode_redsys_parameters(merchant_parameters_b64: str) -> Dict[str, Any]:
    """Devuelve el JSON contenido en Ds_MerchantParameters."""

    decoded = base64.b64decode(merchant_parameters_b64)
    return json.loads(decoded.decode("utf-8"))
