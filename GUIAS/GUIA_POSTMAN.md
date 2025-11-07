# Ejemplo de Petición para Postman

## Configuración de la Petición

### Método y URL
- **Método**: `POST`
- **URL**: `https://suitechredsys.azurewebsites.net/api/encryptdata`

### Headers
- **Content-Type**: `application/json`

### Body (raw JSON)

```json
{
    "urlBC": "https://bc.example.com/api/endpoint",
    "authType": "Basic",
    "user": "usuario_bc",
    "pass": "contraseña_bc",
    "encryptType": "SHA-256",
    "encryptKey": "clave_secreta",
    "encryptData": "datos_a_encriptar"
}
```

## Campos Requeridos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `urlBC` | string | ✅ Sí | URL de BC para reenviar datos después |
| `authType` | string | ✅ Sí | Tipo de autenticación: `"Basic"` o `"oAuth"` |
| `user` | string | ✅ Sí | Usuario para autenticación |
| `pass` | string | ✅ Sí | Contraseña para autenticación |
| `encryptData` | string | ✅ Sí | Datos a encriptar |
| `encryptType` | string | ❌ No | Tipo de encriptación: `"SHA-256"` (por defecto) o `"SHA-512"` |
| `encryptKey` | string | ❌ No | Clave para encriptar/desencriptar (por defecto: cadena vacía) |

## Ejemplo de Respuesta Exitosa

```json
{
    "encryptedData": "fa092d65e6af8ccd74444e3386c19d485c5141e76142446cb83e559e4bdd0294",
    "id": "2425ac23-a24c-4c3c-b0fc-1524d1554834"
}
```

## Ejemplo con SHA-512

```json
{
    "urlBC": "https://bc.example.com/api/endpoint",
    "authType": "Basic",
    "user": "usuario_bc",
    "pass": "contraseña_bc",
    "encryptType": "SHA-512",
    "encryptKey": "clave_secreta",
    "encryptData": "datos_a_encriptar"
}
```

## Ejemplo con oAuth

```json
{
    "urlBC": "https://bc.example.com/api/endpoint",
    "authType": "oAuth",
    "user": "usuario_bc",
    "pass": "contraseña_bc",
    "encryptType": "SHA-256",
    "encryptKey": "clave_secreta",
    "encryptData": "datos_a_encriptar"
}
```

## Errores Comunes

### Error: "Missing field 'urlBC'"
**Causa**: El body no contiene el campo `urlBC` o está mal escrito.

**Solución**: Asegúrate de que el body esté en formato JSON y contenga todos los campos requeridos.

### Error: "Invalid 'authType'. Must be 'Basic' or 'oAuth'"
**Causa**: El campo `authType` tiene un valor incorrecto.

**Solución**: Usa exactamente `"Basic"` o `"oAuth"` (respetando mayúsculas/minúsculas).

### Error: "Invalid 'encryptType'. Must be 'SHA-256' or 'SHA-512'"
**Causa**: El campo `encryptType` tiene un valor incorrecto.

**Solución**: Usa exactamente `"SHA-256"` o `"SHA-512"` (respetando mayúsculas/minúsculas).

## Pasos en Postman

1. Abre Postman
2. Crea una nueva petición POST
3. Ingresa la URL: `https://suitechredsys.azurewebsites.net/api/encryptdata`
4. Ve a la pestaña **Headers**
5. Agrega el header: `Content-Type: application/json`
6. Ve a la pestaña **Body**
7. Selecciona **raw** y **JSON** en el dropdown
8. Pega el JSON de ejemplo arriba
9. Haz clic en **Send**

