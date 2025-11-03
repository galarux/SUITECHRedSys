# 🎯 Objetivo

Crea una **Azure Function en Python** llamada `EncryptData` dentro de un proyecto llamado `SUITECHRedSys`.

De momento, **solo debe hacer una cosa**:  
recibir un dato en el cuerpo de la petición (`data`, `encryptType`, `encryptKey`)  
y devolver el texto encriptado según el tipo indicado (`SHA-256` o `SHA-512`).

---

# 🧩 Estructura del proyecto esperada

```
SUITECHRedSys/
│
├── EncryptData/
│   ├── __init__.py
│   └── function.json
│
├── utils/
│   └── crypto.py
│
├── requirements.txt
├── host.json
└── local.settings.json
```

---

# 🐍 Requisitos de Python

`requirements.txt`
```txt
azure-functions
```

---

# 🔐 Lógica de encriptación

Archivo: `utils/crypto.py`

```python
import hashlib

def encrypt(data: str, key: str, encrypt_type: str) -> str:
    message = (data + key).encode("utf-8")
    if encrypt_type.upper() == "SHA-512":
        return hashlib.sha512(message).hexdigest()
    return hashlib.sha256(message).hexdigest()
```

---

# ⚙️ Azure Function — EncryptData

Archivo: `EncryptData/__init__.py`

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

---

# 🔧 Configuración base

Archivo: `local.settings.json`

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

Archivo: `host.json`

```json
{
  "version": "2.0"
}
```

Archivo: `EncryptData/function.json`

```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"],
      "route": "EncryptData"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

---

# 🧪 Ejemplo de prueba (curl o Postman)

```bash
curl -X POST http://localhost:7071/api/EncryptData \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"hola mundo\",\"encryptType\":\"SHA-256\",\"encryptKey\":\"clave123\"}"
```

**Respuesta esperada:**
```json
{
  "encryptedData": "a91b63b4a1f5b4d..."
}
```

---

# ✅ Instrucciones para Cursor

1. Crea la estructura de carpetas y archivos indicada.
2. Inserta el contenido exacto de cada bloque.
3. No agregues todavía lógica de almacenamiento ni conexión con BC o RedSys.
4. El resultado debe poder ejecutarse con `func start` y devolver el texto encriptado.
