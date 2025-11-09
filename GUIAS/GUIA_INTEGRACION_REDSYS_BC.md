# Guía Integración RedSys ↔ Business Central

## 1. Registro y permisos en Entra ID
- Entra ID → `Registros de aplicaciones` → `Nuevo registro` (`Single tenant`).
- Crear secreto en `Certificados y secretos`; guardar `client_id`, `tenant_id`, valor del secreto, caducidad.
- `Permisos de API` → `Dynamics 365 Business Central` → permisos de aplicación (`API.ReadWrite.All` y `Automation.ReadWrite.All` si procede). Conceder consentimiento de administrador.
- En `Autenticación` añadir redirect URI: `https://businesscentral.dynamics.com/OAuthLanding.htm`.

## 2. Autorización en Business Central
- Acceder al entorno (web client) como admin.
- Buscar `Azure Active Directory Applications`.
- Crear nuevo registro con el `client_id`, marcar empresa o permitir todas, asignar conjunto de permisos (por ejemplo `D365 BUS FULL ACCESS`), activar y conceder consentimiento cuando lo solicite.

## 3. Prueba de token con Postman
- Crear environment con variables `tenant_id`, `client_id`, `client_secret`, `environment_name`.
- Request `POST https://login.microsoftonline.com/{{tenant_id}}/oauth2/v2.0/token` con body `x-www-form-urlencoded`:
  - `grant_type=client_credentials`
  - `client_id={{client_id}}`
  - `client_secret={{client_secret}}`
  - `scope=https://api.businesscentral.dynamics.com/.default`
- Guardar `access_token` y validar con `GET https://api.businesscentral.dynamics.com/v2.0/{{tenant_id}}/{{environment_name}}/api/v2.0/companies`.

## 4. Azure Functions

### 4.1 `EncryptData`
- Endpoint: `POST /api/EncryptData`.
- Campos mínimos en el body:
  - `urlBC`: URL del endpoint de BC (ej. `https://api.businesscentral.dynamics.com/v2.0/<tenant>/<env>/api/v2.0/notifications`).
  - `authType`: `oAuth` o `Basic`.
  - `user`: para `oAuth` = `client_id`; para `Basic` = usuario.
  - `pass`: para `oAuth` = `client_secret`; para `Basic` = contraseña.
  - `encryptData`: texto a cifrar.
  - `Ds_Merchant_Order`: código de pedido empleado para vincular la notificación.
  - Opcionales: `encryptType`, `encryptKey`, `bcMethod` (por defecto `POST`), `bcPath` (ruta relativa en BC).
- La función cifra `encryptData`, guarda la configuración en Table Storage (`EncryptDataLogs`) incluyendo credenciales, método y path, y devuelve `encryptedData` + `id`.

### 4.2 `BCCompanies`
- Endpoint auxiliar para pruebas: `GET /api/bc/companies`.
- Lee el registro de Table Storage usando `order`, obtiene token con la configuración guardada y llama a BC (`method/path` configurables). Devuelve la respuesta de Business Central.

### 4.3 `DecryptAndRedirect`
- Endpoint: `POST /api/DecryptAndRedirect`.
- Procesa notificaciones RedSys:
  - Extrae `Ds_MerchantParameters` y `Ds_Signature`.
  - Valida firma con `REDSYS_SHA256_KEY`.
  - Recupera la configuración en Table Storage (según `Ds_Order`).
  - Si `AuthType = oAuth`, obtiene token; si `Basic`, usa las credenciales.
  - Envía a BC (método/ruta definidos) el payload:
    ```json
    {
      "merchantParameters": { ...datos decodificados... },
      "merchantParametersRaw": "<Base64 original>",
      "signature": "<firma recibida>",
      "order": "<Ds_Order>"
    }
    ```
  - Devuelve resumen de la llamada y cualquier error de BC.

## 5. Tabla y API en Business Central

### Tabla `RedSys Notification` (objeto 50100)
- Campos sugeridos:
  - `Order` (PK) – `Code[20]`
  - `Merchant Code` – `Code[15]`
  - `Terminal` – `Code[3]`
  - `Amount` – `Decimal`, 2 decimales
  - `Currency`, `Transaction Type`, `Response Code`, `Authorization Code`
  - `Secure Payment` (Boolean), `Card Number`, `Consumer Language`, `Merchant Data`
  - `Notification Date Time` (DateTime) -> combinando `Ds_Date` + `Ds_Hour`
  - `Raw Parameters` (Blob/Text) – `merchantParametersRaw`
  - `JSON Payload` (Blob/Text) – contenido completo `merchantParameters`
  - `Signature`, `Status` (Option: Pending/Processed/Error), `Processing Message`

### Page API `RedSys Notification API` (objeto 50100)
- Tipo `API`, ruta `/suitech/redsys/v1.0/notifications`.
- `InsertAllowed = true`, `Modify/Delete = false`.
- Exponer los campos anteriores; en `OnInsert` establecer `Status := Status::Pending` si corresponde.

## 6. Flujo end-to-end
1. Registrar app en Entra ID + BC, obtener token y verificar en Postman.
2. Guardar configuración mediante `EncryptData` (incluye `bcMethod` y `bcPath` de la API personalizada).
3. Configurar en RedSys la URL de notificación: `https://<function-app>.azurewebsites.net/api/DecryptAndRedirect?code=<function-key>`.
4. RedSys envía notificación.
5. `DecryptAndRedirect` valida, llama a BC y la Page API inserta la notificación en la tabla.
6. Revisar logs en Application Insights/Azure Portal (`GUIA_VER_LOGS_AZURE.md`) para monitorizar.

## 7. Pruebas recomendadas
- Notificación válida (firma correcta) → verifica que el registro aparece en BC.
- Notificación con firma incorrecta → la función responde 401, no se llama a BC.
- Error de BC (por ejemplo, path incorrecto) → la respuesta muestra `bcCall.status` con código >= 400.

## 8. Seguridad y despliegue
- Mover `client_secret` y otros secretos a Azure Key Vault o App Settings con `slot setting`.
- Revisar `requirements.txt` (`requests` añadido).
- Ejecutar pruebas con RedSys Sandbox antes de producción.
- Actualizar documentación de despliegue (`GUIA_PUBLICAR_AZURE.md`) con la nueva función si aplica.

