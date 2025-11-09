import base64
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.crypto import compute_redsys_signature  # noqa: E402


def generate(order: str, terminal_key: str, template: dict | None = None) -> tuple[str, str]:
    """Genera Ds_MerchantParameters y Ds_Signature para pruebas."""
    base_payload = {
        "Ds_Date": "09/11/2025",
        "Ds_Hour": "21:30",
        "Ds_SecurePayment": "1",
        "Ds_Card_Country": "724",
        "Ds_Amount": "900",
        "Ds_Currency": "978",
        "Ds_Order": order,
        "Ds_MerchantCode": "263100000",
        "Ds_Terminal": "049",
        "Ds_Response": "0000",
        "Ds_MerchantData": "",
        "Ds_TransactionType": "38",
        "Ds_ConsumerLanguage": "1",
        "Ds_AuthorisationCode": "333982",
        "Ds_Card_Brand": "1",
        "Ds_Card_Typology": "CONSUMO",
        "Ds_ProcessedPayMethod": "78",
        "Ds_Titular": "Daniel",
        "Ds_Control_1762720119985": "1762720119985",
    }

    if template:
        base_payload.update(template)
        base_payload["Ds_Order"] = order

    params_b64 = base64.b64encode(json.dumps(base_payload).encode("utf-8")).decode("utf-8")
    signature = compute_redsys_signature(params_b64, order, terminal_key)
    return params_b64, signature


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/generate_redsys_payload.py <ORDER> <REDSYS_SHA256_KEY_BASE64>")
        sys.exit(1)

    order_arg = sys.argv[1]
    key_arg = sys.argv[2]

    params, sign = generate(order_arg, key_arg)

    print("Ds_MerchantParameters:", params)
    print("Ds_Signature:", sign)

