import hashlib

def encrypt(data: str, key: str, encrypt_type: str) -> str:
    message = (data + key).encode("utf-8")
    if encrypt_type.upper() == "SHA-512":
        return hashlib.sha512(message).hexdigest()
    return hashlib.sha256(message).hexdigest()
