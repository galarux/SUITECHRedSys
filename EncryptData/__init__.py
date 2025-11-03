import azure.functions as func
import json
from utils.crypto import encrypt

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        data = body.get("data")
        encrypt_type = body.get("encryptType", "SHA-256")
        encrypt_key = body.get("encryptKey", "")

        if not data:
            return func.HttpResponse(
                json.dumps({"error": "Missing field 'data'"}),
                mimetype="application/json",
                status_code=400
            )

        result = encrypt(data, encrypt_key, encrypt_type)
        return func.HttpResponse(
            json.dumps({"encryptedData": result}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
