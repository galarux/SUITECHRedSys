# 🔐 SUITECHRedSys - EncryptData

Azure Function en Python que encripta datos usando algoritmos SHA-256 o SHA-512.

## 📋 Descripción

Esta Azure Function recibe datos a través de una petición HTTP POST y devuelve el texto encriptado según el algoritmo especificado (SHA-256 o SHA-512).

## 🚀 Características

- ✅ Encriptación SHA-256
- ✅ Encriptación SHA-512
- ✅ Endpoint HTTP POST
- ✅ Respuestas JSON
- ✅ Manejo de errores

## 🛠️ Requisitos

- Python 3.12.4 o superior
- Azure Functions Core Tools 4.4.0 o superior
- npm (para instalar Azure Functions Core Tools)

## 📦 Instalación

1. **Clonar el repositorio:**
```bash
git clone <url-del-repositorio>
cd SUITECH-RedSys
```

2. **Crear y activar el entorno virtual:**
```bash
python -m venv venv

# En PowerShell (Windows)
.\venv\Scripts\Activate.ps1

# En CMD (Windows)
venv\Scripts\activate.bat

# En Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Instalar Azure Functions Core Tools (si no está instalado):**
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

## 🏃 Ejecución Local

1. **Iniciar la función:**
```bash
func start
```

2. **La función estará disponible en:**
```
http://localhost:7071/api/EncryptData
```

## 📡 Uso de la API

### Endpoint
```
POST http://localhost:7071/api/EncryptData
```

### Headers
```
Content-Type: application/json
```

### Body (JSON)
```json
{
  "data": "texto a encriptar",
  "encryptType": "SHA-256",
  "encryptKey": "clave secreta"
}
```

### Parámetros
- **data** (requerido): Texto a encriptar
- **encryptType** (opcional): Tipo de encriptación (`SHA-256` o `SHA-512`). Por defecto: `SHA-256`
- **encryptKey** (opcional): Clave adicional para la encriptación. Por defecto: `""`

### Respuesta Exitosa (200 OK)
```json
{
  "encryptedData": "hash_encriptado_aqui"
}
```

### Respuesta de Error (400/500)
```json
{
  "error": "Mensaje de error"
}
```

## 🧪 Ejemplos

### Con PowerShell
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'; $response.Content
```

### Con curl
```bash
curl -X POST http://localhost:7071/api/EncryptData \
  -H "Content-Type: application/json" \
  -d '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'
```

### Con Postman
- **Método:** POST
- **URL:** `http://localhost:7071/api/EncryptData`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "data": "hola mundo",
  "encryptType": "SHA-256",
  "encryptKey": "clave123"
}
```

## 📁 Estructura del Proyecto

```
SUITECHRedSys/
│
├── EncryptData/
│   ├── __init__.py          # Lógica principal de la función
│   └── function.json        # Configuración del trigger HTTP
│
├── utils/
│   └── crypto.py            # Lógica de encriptación
│
├── venv/                    # Entorno virtual (no commitear)
├── requirements.txt         # Dependencias del proyecto
├── host.json               # Configuración del host
├── local.settings.json     # Configuración local (no commitear)
├── .gitignore              # Archivos ignorados por git
├── README.md               # Este archivo
├── GUIA_DESARROLLO.md      # Guía de desarrollo
└── SUITECHRedSys_EncryptData.md  # Especificaciones del proyecto
```

## 📚 Documentación Adicional

- Consulta `GUIA_DESARROLLO.md` para instrucciones detalladas de desarrollo
- Consulta `SUITECHRedSys_EncryptData.md` para las especificaciones técnicas

## 📝 Notas

- **local.settings.json** no debe commitearse a git (ya está en .gitignore)
- El entorno virtual **venv/** no debe commitearse a git (ya está en .gitignore)

## 🔒 Seguridad

⚠️ Esta función está configurada con `authLevel: "anonymous"` para desarrollo local. Asegúrate de configurar la autenticación adecuada antes de desplegar en producción.

## 📄 Licencia

[Especificar licencia si aplica]
