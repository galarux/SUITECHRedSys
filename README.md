# SUITECH RedSys Functions

Azure Functions en Python que conectan Business Central con RedSys.

## Endpoints

### EncryptData
- `POST /api/EncryptData`
- Body mínimo:
  ```json
  {
    "urlBC": "https://.../api/.../notifications",
    "authType": "Basic" | "oAuth",
    "user": "...",
    "pass": "...",
    "encryptData": "...",
    "encryptKey": "<REDSYS_SHA256_KEY>",
    "Ds_Merchant_Order": "ORDER001"
  }
  ```
- Devuelve `encryptedData` y guarda la configuración en `EncryptDataLogs` (contraseña cifrada con la clave RedSys).

### DecryptAndRedirect
- `POST /api/DecryptAndRedirect`
- Recibe `Ds_SignatureVersion`, `Ds_MerchantParameters`, `Ds_Signature`.
- Valida la firma con `REDSYS_SHA256_KEY`, busca el pedido, llama a BC con la URL/credenciales guardadas y añade los payloads como streams cuando procede.

## Ejecución local
1. Configura `local.settings.json` con `AzureWebJobsStorage` y `REDSYS_SHA256_KEY`.
2. Instala dependencias: `pip install -r requirements.txt`.
3. Arranca: `func start`.
4. Endpoints locales: `http://localhost:7071/api/EncryptData` y `http://localhost:7071/api/DecryptAndRedirect`.

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
- Los cambios en `GUIAS/` se ignoran en Git (solo documentación interna).
- Si necesitas reconfigurar credenciales, repite la llamada a `EncryptData` con el nuevo pedido.
