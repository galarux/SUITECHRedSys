# SUITECH RedSys Functions

Azure Functions en Python que conectan Business Central con RedSys.

## Endpoints

### DecryptAndRedirect
- `POST /api/DecryptAndRedirect`
- Recibe `Ds_SignatureVersion`, `Ds_MerchantParameters`, `Ds_Signature`.
- Valida la firma con `REDSYS_SHA256_KEY`, busca el pedido, llama a BC con la URL/credenciales guardadas y añade los payloads como streams cuando procede.

### PaygoldLink
- `POST /api/PaygoldLink`
- Genera un enlace Paygold siguiendo la documentación oficial de RedSys ([Firmar una operación](https://pagosonline.redsys.es/desarrolladores-inicio/documentacion-operativa/firmar-una-operacion/)). La función compone `Ds_MerchantParameters`, deriva la clave con AES-CBC y calcula la firma HMAC-SHA256 (`HMAC_SHA256_V1`) antes de llamar al endpoint indicado (`redirectURL`).
- Ejemplo completo listo para Postman:
  ```json
  {
    "urlBC": "https://api.businesscentral.dynamics.com/v2.0/{{tenant_id}}/{{enviroment_name}}/api/galarux/redsys/v1.0/companies({{company_id_oauth}})/notifications",
    "authType": "oAuth",
    "user": "{{client_id_oauth}}",
    "pass": "{{client_secret_oauth}}",
    "encryptData": {
      "DS_MERCHANT_AMOUNT": "1",
      "DS_MERCHANT_CURRENCY": "978",
      "DS_MERCHANT_CUSTOMER_MAIL": "daniel.oton@gmail.com",
      "DS_MERCHANT_CUSTOMER_MOBILE": "669267159",
      "DS_MERCHANT_MERCHANTCODE": "263100000",
      "DS_MERCHANT_ORDER": "suihgr001",
      "DS_MERCHANT_TRANSACTIONTYPE": "0",
      "DS_MERCHANT_PAYGOLD": "true",
      "DS_MERCHANT_TERMINAL": "49",
    },
    "redirectURL": "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST",
    "encryptKey": "sq7HjrUOBfKmC576ILgskD5srU870gJ7"
  }
  ```
- El objeto `encryptData` admite cualquier campo `DS_...` permitido por RedSys. Para Paygold, indica `"paygold": true` en el body o envía explícitamente `DS_MERCHANT_PAYGOLD`. Si no lo haces, la operación se tratará como un pago REST estándar.
- La función reutiliza variables de entorno (`REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_CURRENCY`/`PAYGOLD_CURRENCY`, `REDSYS_REST_URL`/`PAYGOLD_REST_URL`, `PAYGOLD_SHA256_KEY`/`REDSYS_SHA256_KEY`) en caso de que la petición no las aporte.
- Al finalizar, la respuesta contiene el JSON de RedSys (`Ds_PayURL`, etc.), además del `entityId` almacenado en `EncryptDataLogs` junto a la configuración de Business Central.

## Ejecución local
1. Configura `local.settings.json` con `AzureWebJobsStorage` y `REDSYS_SHA256_KEY`.
2. Instala dependencias: `pip install -r requirements.txt`.
3. Arranca: `func start`.
4. Endpoints locales: `http://localhost:7071/api/DecryptAndRedirect` y `http://localhost:7071/api/PaygoldLink`.

## Despliegue rápido
```bash
func azure functionapp publish suitechredsys --python
```
Variables obligatorias en la Function App: `AzureWebJobsStorage`, `REDSYS_SHA256_KEY`, `REDSYS_MERCHANT_CODE`, `REDSYS_TERMINAL`, `REDSYS_REST_URL` y `REDSYS_NOTIFICATION_URL`.

## Utilidades
- `tools/generate_redsys_payload.py ORDER123 <REDSYS_SHA256_KEY>` genera `Ds_MerchantParameters` y firma para pruebas locales.
- `utils/crypto.py` incluye el cifrado AES-GCM para credenciales y las rutinas RedSys.

## Notas
- La tabla `EncryptDataLogs` se crea automáticamente.
