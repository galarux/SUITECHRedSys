import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Intentar importar utils.crypto
        try:
            from utils.crypto import encrypt
        except ImportError as import_error:
            logging.error(f"Error al importar utils.crypto: {str(import_error)}")
            return func.HttpResponse(
                json.dumps({"error": f"Error al importar módulo: {str(import_error)}"}),
                mimetype="application/json",
                status_code=500
            )
        
        # Intentar importar utils.table_storage_sdk
        try:
            from utils.table_storage_sdk import save_to_table
        except ImportError as import_error:
            logging.warning(f"Error al importar utils.table_storage_sdk: {str(import_error)}")
            save_to_table = None
        
        body = req.get_json()
        
        # Extraer todos los campos requeridos del body
        url_bc = body.get("urlBC")
        auth_type = body.get("authType")
        user = body.get("user")
        password = body.get("pass")
        encrypt_type = body.get("encryptType", "SHA-256")
        encrypt_key = body.get("encryptKey", "")
        encrypt_data = body.get("encryptData")
        ds_merchant_order = body.get("Ds_Merchant_Order") or body.get("dsMerchantOrder")

        # Validar campos requeridos
        if not url_bc:
            error_msg = "Missing field 'urlBC'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )
        
        if not auth_type:
            error_msg = "Missing field 'authType'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )
        
        if auth_type not in ["Basic", "oAuth"]:
            error_msg = "Invalid 'authType'. Must be 'Basic' or 'oAuth'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )
        
        if not user:
            error_msg = "Missing field 'user'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )
        
        if not password:
            error_msg = "Missing field 'pass'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )
        
        if not encrypt_data:
            error_msg = "Missing field 'encryptData'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )
        
        if encrypt_type not in ["SHA-256", "SHA-512"]:
            error_msg = "Invalid 'encryptType'. Must be 'SHA-256' or 'SHA-512'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )

        if not encrypt_key:
            error_msg = "Missing field 'encryptKey'"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=400
            )

        # Encriptar los datos
        result = encrypt(encrypt_data, encrypt_key, encrypt_type)
        
        # Guardar datos de conexión BC en la tabla usando SDK directamente
        entity_id = None
        if save_to_table:
            try:
                entity_id = save_to_table(
                    url_bc=url_bc,
                    auth_type=auth_type,
                    user=user,
                    password=password,
                    encrypt_type=encrypt_type,
                    encrypt_key=encrypt_key,
                    ds_merchant_order=ds_merchant_order
                )
            except Exception as table_error:
                logging.error("Error al guardar en tabla: %s", table_error)
                return func.HttpResponse(
                    json.dumps({"error": "No se pudo persistir la configuración en Table Storage"}),
                    mimetype="application/json",
                    status_code=500
                )
        
        return func.HttpResponse(
            json.dumps({
                "encryptedData": result,
                "id": entity_id
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error en EncryptData: {error_msg}")
        
        # Intentar guardar error en la tabla si tenemos datos mínimos
        try:
            body = req.get_json() if req else {}
            if body.get("urlBC") and save_to_table:
                save_to_table(
                    url_bc=body.get("urlBC", ""),
                    auth_type=body.get("authType", ""),
                    user=body.get("user", ""),
                    password=body.get("pass", ""),
                    encrypt_type=body.get("encryptType", "SHA-256"),
                    encrypt_key=body.get("encryptKey", ""),
                    ds_merchant_order=body.get("Ds_Merchant_Order") or body.get("dsMerchantOrder"),
                    error=error_msg
                )
        except Exception as log_error:
            logging.error(f"Error al guardar en tabla: {str(log_error)}")
        
        return func.HttpResponse(
            json.dumps({"error": error_msg}),
            mimetype="application/json",
            status_code=500
        )
