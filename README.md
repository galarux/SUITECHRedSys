# 🔐 SUITECHRedSys - EncryptData

Azure Function en Python diseñada para encriptar datos mediante algoritmos SHA-256 o SHA-512 y servir como base para el flujo de integración entre Business Central (BC) y RedSys.

## 🎯 Objetivo y Alcance

### Objetivo actual

Implementar el endpoint `EncryptData`, que recibe un cuerpo JSON con los campos `data`, `encryptType` y `encryptKey`, aplica la encriptación solicitada (`SHA-256` o `SHA-512`) y devuelve el resultado en formato JSON.

### Objetivo futuro (definido con el cliente)

Desarrollar dos endpoints dentro de la misma Azure Function:

- `EncryptData`: llamado desde BC para encriptar información y almacenar metadatos de la conexión.
- `DecryptAndRedirect`: llamado desde RedSys para desencriptar la información asociada a un identificador, recuperar los datos almacenados y reenviar la información a BC.

## 🚀 Características

- ✅ Encriptación SHA-256 y SHA-512.
- ✅ Endpoint HTTP POST (`EncryptData`).
- ✅ Respuestas JSON con manejo básico de errores.
- ✅ Preparado para ampliarse con lógica de persistencia y nuevos endpoints.

## 🧩 Arquitectura y Estructura

```
SUITECHRedSys/
│
├── EncryptData/
│   ├── __init__.py          # Lógica principal del endpoint EncryptData
│   └── function.json        # Configuración del trigger HTTP
│
├── utils/
│   └── crypto.py            # Funciones de encriptación
│
├── requirements.txt         # Dependencias Python
├── host.json                # Configuración general del host
├── local.settings.json      # Configuración local (no versionar)
├── extensions.csproj        # Extensiones de Azure Functions (bindings)
├── GUIAS/                   # Documentación complementaria
├── README.md                # Este documento unificado
└── ...                      # Otros recursos del proyecto
```

### Componentes clave

- `utils/crypto.py`

  ```python
  import hashlib

  def encrypt(data: str, key: str, encrypt_type: str) -> str:
      message = (data + key).encode("utf-8")
      if encrypt_type.upper() == "SHA-512":
          return hashlib.sha512(message).hexdigest()
      return hashlib.sha256(message).hexdigest()
  ```

- `EncryptData/__init__.py`

  ```python
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
  ```

## 🛠️ Requisitos

### Herramientas

- Python 3.12.4 o superior.
- Azure Functions Core Tools 4.4.0 o superior.
- npm (para instalar Azure Functions Core Tools).
- Azure CLI (para despliegue en Azure).

### Dependencias Python

`requirements.txt`

```txt
azure-functions
```

## 📦 Instalación y Configuración

1. **Clonar el repositorio**

   ```bash
   git clone <url-del-repositorio>
   cd SUITECH-RedSys
   ```

2. **Crear y activar un entorno virtual**

   ```bash
   python -m venv venv

   # PowerShell (Windows)
   .\venv\Scripts\Activate.ps1

   # CMD (Windows)
   venv\Scripts\activate.bat

   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instalar dependencias del proyecto**

   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar Azure Functions Core Tools (si no está instalado)**

   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

## 🏃 Ejecución Local

1. **Iniciar la función**

   ```bash
   func start
   ```

2. **Endpoint local disponible**

   ```
   http://localhost:7071/api/EncryptData
   ```

## ☁️ Despliegue en Azure

### Requisitos previos

- Haber iniciado sesión con `az login`.
- Disponer de una suscripción de Azure activa.
- Tener instaladas las Azure Functions Core Tools.

### Publicar la Function App

1. Crear (o verificar) la Function App en Azure:
   - Resource group: `rg-suitech-redsys` (ejemplo).
   - Function App name: debe ser único globalmente.
   - Runtime: Python 3.12.
   - Sistema operativo: Linux.
   - Plan: Consumption (Serverless).

2. Publicar desde local:

   ```bash
   func azure functionapp publish <nombre-function-app> --python
   ```

### URL de producción (actual)

``` 
https://suitechredsys.azurewebsites.net/api/encryptdata
```

## 📡 Uso del Endpoint `EncryptData`

### Endpoints

- Local: `POST http://localhost:7071/api/EncryptData`
- Producción: `POST https://suitechredsys.azurewebsites.net/api/encryptdata?code=<function-key>`

### Headers

```text
Content-Type: application/json
```

### Cuerpo esperado

```json
{
  "data": "texto a encriptar",
  "encryptType": "SHA-256",
  "encryptKey": "clave secreta"
}
```

### Parámetros

- `data` (obligatorio): texto plano.
- `encryptType` (opcional): `SHA-256` o `SHA-512`. Valor predeterminado `SHA-256`.
- `encryptKey` (opcional): clave adicional para generar el hash. Por defecto cadena vacía.

### Respuestas

```json
{
  "encryptedData": "hash_encriptado_aqui"
}
```

Errores (400/500):

```json
{
  "error": "Mensaje de error"
}
```

### Ejemplos rápidos

- **PowerShell (Local)**

  ```powershell
  $response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'; $response.Content
  ```

- **PowerShell (Producción)**

  ```powershell
  $functionKey = "<function-key>"
  $url = "https://suitechredsys.azurewebsites.net/api/encryptdata?code=$functionKey"
  $response = Invoke-WebRequest -Uri $url -Method POST -ContentType "application/json" -Body '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'; $response.Content
  ```

- **curl**

  ```bash
  curl -X POST http://localhost:7071/api/EncryptData \
    -H "Content-Type: application/json" \
    -d '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'
  ```

- **Postman**
  - Método: POST
  - URL local: `http://localhost:7071/api/EncryptData`
  - URL producción: `https://suitechredsys.azurewebsites.net/api/encryptdata?code=<function-key>` o usa header `x-functions-key` con la misma clave.
  - Headers: `Content-Type: application/json`
  - Body (raw JSON): mismo payload que en los ejemplos anteriores.

## 📊 Datos que manejará la solución completa

### Entrada desde BC hacia `EncryptData`

- `urlBC`
- `authType` (`Basic` u `oAuth`)
- `user`
- `pass`
- `encryptType` (`SHA-256` o `SHA-512`)
- `encryptKey`
- `encryptData` (contenido a encriptar)

### Tabla de almacenamiento prevista

- `Id`
- `urlBC`
- `authType`
- `user`
- `pass`
- `encryptType`
- `encryptKey`

### Llamada esperada desde RedSys hacia `DecryptAndRedirect`

```
GET https://<function-app>.azurewebsites.net/api/RedSysResponse?id=<id>
```

La función deberá localizar el registro en la tabla, desencriptar la información de RedSys con la `encryptKey` correspondiente y reenviarla a la URL almacenada de BC con las credenciales asociadas.

## 🧪 Escenarios de prueba

```bash
curl -X POST http://localhost:7071/api/EncryptData \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"hola mundo\",\"encryptType\":\"SHA-256\",\"encryptKey\":\"clave123\"}"
```

Respuesta esperada:

```json
{
  "encryptedData": "a91b63b4a1f5b4d..."
}
```

## 📝 Notas de desarrollo

- `local.settings.json` y el directorio `venv/` no deben versionarse (ya están listados en `.gitignore`).
- `authLevel` está configurado en `function`; necesitas incluir la `function key` (`?code=<clave>` o header `x-functions-key`) para invocar el endpoint desplegado.
- El archivo `extensions.csproj` mantiene las extensiones/bindings necesarios; no eliminar si se usa almacenamiento, colas u otros triggers.

## 📚 Documentación de apoyo

- Carpeta `GUIAS/` con guías específicas (desarrollo, pruebas, publicación, etc.).
- Documentación oficial:
  - PayGold vía REST | Redsys | Desarrolladores TPVV
  - Autenticación | Redsys | Desarrolladores TPVV
  - PayGold | API - Developers Docs

## 📄 Anexo: requisitos originales del cliente

> "Hay que crear una Azure Function (a partir de ahora AF) con dos funcionalidades que van a ser dos endpoints [...]."

Este anexo recoge el alcance acordado inicialmente con el cliente para facilitar el seguimiento de futuras ampliaciones.
