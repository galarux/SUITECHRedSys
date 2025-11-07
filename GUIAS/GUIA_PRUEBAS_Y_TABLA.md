# 🧪 Guía de Pruebas y Visualización de Tabla

Esta guía explica cómo probar la función `EncryptData` y cómo visualizar el contenido de la tabla Azure Table Storage.

---

## 🚀 Paso 1: Iniciar la Función Localmente

### Prerrequisitos
- Entorno virtual activado
- Dependencias instaladas (`pip install -r requirements.txt`)
- Azure Functions Core Tools instalado

### Iniciar la función

**En PowerShell:**
```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar la función
func start
```

**En CMD:**
```cmd
venv\Scripts\activate.bat
func start
```

**En Linux/Mac:**
```bash
source venv/bin/activate
func start
```

Deja esta terminal corriendo. La función estará disponible en:
```
http://localhost:7071/api/EncryptData
```

---

## 🧪 Paso 2: Probar la Función

### ⚠️ IMPORTANTE: Formato del Body

La función ahora requiere estos campos en el body:

```json
{
  "urlBC": "https://bc.example.com/api/endpoint",
  "authType": "Basic",
  "user": "usuario_bc",
  "pass": "contraseña_bc",
  "encryptType": "SHA-256",
  "encryptKey": "clave_secreta",
  "encryptData": "datos a encriptar"
}
```

### Opción 1: PowerShell (Recomendado en Windows)

**Comando completo:**
```powershell
$body = @{
    urlBC = "https://bc.example.com/api/endpoint"
    authType = "Basic"
    user = "usuario_bc"
    pass = "contraseña_bc"
    encryptType = "SHA-256"
    encryptKey = "clave_secreta"
    encryptData = "datos a encriptar"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body $body
$response.Content
```

**Versión en una línea:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.example.com/api/endpoint","authType":"Basic","user":"usuario_bc","pass":"contraseña_bc","encryptType":"SHA-256","encryptKey":"clave_secreta","encryptData":"datos a encriptar"}'; $response.Content
```

**Prueba con SHA-512:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.example.com/api/endpoint","authType":"Basic","user":"usuario_bc","pass":"contraseña_bc","encryptType":"SHA-512","encryptKey":"clave_secreta","encryptData":"datos a encriptar"}'; $response.Content
```

**Prueba con oAuth:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.example.com/api/endpoint","authType":"oAuth","user":"usuario_bc","pass":"contraseña_bc","encryptType":"SHA-256","encryptKey":"clave_secreta","encryptData":"datos a encriptar"}'; $response.Content
```

### Opción 2: curl (PowerShell)

```powershell
curl -X POST http://localhost:7071/api/EncryptData `
  -H "Content-Type: application/json" `
  -d '{\"urlBC\":\"https://bc.example.com/api/endpoint\",\"authType\":\"Basic\",\"user\":\"usuario_bc\",\"pass\":\"contraseña_bc\",\"encryptType\":\"SHA-256\",\"encryptKey\":\"clave_secreta\",\"encryptData\":\"datos a encriptar\"}'
```

### Opción 3: curl (CMD o Git Bash)

```bash
curl -X POST http://localhost:7071/api/EncryptData \
  -H "Content-Type: application/json" \
  -d "{\"urlBC\":\"https://bc.example.com/api/endpoint\",\"authType\":\"Basic\",\"user\":\"usuario_bc\",\"pass\":\"contraseña_bc\",\"encryptType\":\"SHA-256\",\"encryptKey\":\"clave_secreta\",\"encryptData\":\"datos a encriptar\"}"
```

### Opción 4: Postman

1. **Método:** `POST`
2. **URL:** `http://localhost:7071/api/EncryptData`
3. **Headers:**
   - `Content-Type: application/json`
4. **Body (raw JSON):**
```json
{
  "urlBC": "https://bc.example.com/api/endpoint",
  "authType": "Basic",
  "user": "usuario_bc",
  "pass": "contraseña_bc",
  "encryptType": "SHA-256",
  "encryptKey": "clave_secreta",
  "encryptData": "datos a encriptar"
}
```

### Respuesta Esperada (Exitosa)

```json
{
  "encryptedData": "a91b63b4a1f5b4d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

El `id` es el UUID único que se guardó en la tabla y que se usará después para buscar los datos cuando RedSys llame a `DecryptAndRedirect`.

---

## 📊 Paso 3: Ver el Contenido de la Tabla

### Opción 1: Azure Storage Explorer (Recomendado)

**Azure Storage Explorer** es una herramienta de escritorio gratuita que permite ver y gestionar Azure Storage.

#### Instalación
1. Descarga desde: https://azure.microsoft.com/features/storage-explorer/
2. Instala y abre la aplicación

#### Conectar a Azure Storage Emulator (Local)

1. En Azure Storage Explorer, haz clic en **"Add Account"**
2. Selecciona **"Add an account via Azure Storage Emulator"**
3. Se conectará automáticamente al emulador local (Azurite)

#### Ver la Tabla

1. En el panel izquierdo, expande **"Local & Attached"** → **"Storage Accounts"** → **"(Emulator - Default Ports)"** → **"Tables"**
2. Busca la tabla **"EncryptDataLogs"**
3. Haz doble clic para ver las entidades (filas)
4. Verás todas las columnas: `Id`, `URLBC`, `AuthType`, `User`, `Pass`, `EncryptType`, `EncryptKey`, `Timestamp`, etc.

#### Conectar a Azure Storage en la Nube

1. Haz clic en **"Add Account"**
2. Selecciona **"Add an Azure account"**
3. Inicia sesión con tu cuenta de Azure
4. Expande tu suscripción → **Storage Accounts** → [Tu Storage Account] → **Tables**
5. Busca **"EncryptDataLogs"**

---

### Opción 2: Azure Portal

1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca tu **Storage Account**
3. En el menú lateral, selecciona **"Tables"** (o **"Data storage"** → **"Tables"**)
4. Busca la tabla **"EncryptDataLogs"**
5. Haz clic en la tabla para ver las entidades
6. Puedes ver todas las filas y columnas

**Nota:** Azure Portal tiene limitaciones para ver tablas grandes. Para tablas con muchas filas, usa Azure Storage Explorer o Azure CLI.

---

### Opción 3: Azure CLI

#### Instalar Azure CLI (si no está instalado)
```powershell
# Windows (PowerShell)
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; Remove-Item .\AzureCLI.msi
```

#### Consultar la Tabla

```bash
# Autenticarse
az login

# Listar tablas en un Storage Account
az storage table list --account-name <nombre-storage-account> --account-key <storage-key>

# Consultar entidades de la tabla
az storage entity query \
  --table-name EncryptDataLogs \
  --account-name <nombre-storage-account> \
  --account-key <storage-key>
```

**Obtener la Storage Key:**
```bash
az storage account keys list \
  --resource-group <resource-group> \
  --account-name <nombre-storage-account>
```

---

### Opción 4: Script Python para Consultar la Tabla

Crea un archivo `consultar_tabla.py`:

```python
from azure.data.tables import TableServiceClient
from azure.core.credentials import AzureNamedKeyCredential
import os

# Para desarrollo local (Azurite)
connection_string = "UseDevelopmentStorage=true"

# Para Azure en la nube, usa:
# connection_string = "DefaultEndpointsProtocol=https;AccountName=<nombre>;AccountKey=<key>;EndpointSuffix=core.windows.net"

table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
table_client = table_service.get_table_client(table_name="EncryptDataLogs")

# Consultar todas las entidades
entities = table_client.list_entities()
print("Entidades en la tabla EncryptDataLogs:\n")
for entity in entities:
    print(f"ID: {entity.get('Id')}")
    print(f"URL BC: {entity.get('URLBC')}")
    print(f"Auth Type: {entity.get('AuthType')}")
    print(f"User: {entity.get('User')}")
    print(f"Encrypt Type: {entity.get('EncryptType')}")
    print(f"Timestamp: {entity.get('Timestamp')}")
    print("-" * 50)

# Consultar por ID específico
# id_buscado = "550e8400-e29b-41d4-a716-446655440000"
# entity = table_client.get_entity(partition_key="2024-01-15", row_key=id_buscado)
# print(f"Entidad encontrada: {entity}")
```

**Ejecutar el script:**
```bash
# Instalar dependencia si no está instalada
pip install azure-data-tables

# Ejecutar
python consultar_tabla.py
```

---

## 🔍 Estructura de la Tabla

La tabla `EncryptDataLogs` tiene las siguientes columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| **PartitionKey** | String | Fecha en formato `YYYY-MM-DD` |
| **RowKey** | String | UUID único (igual que `Id`) |
| **Id** | String | UUID único generado para cada llamada |
| **URLBC** | String | URL de BC para reenviar datos |
| **AuthType** | String | Tipo de autenticación (`Basic` o `oAuth`) |
| **User** | String | Usuario para autenticación |
| **Pass** | String | Contraseña para autenticación |
| **EncryptType** | String | Tipo de encriptación (`SHA-256` o `SHA-512`) |
| **EncryptKey** | String | Clave para encriptar/desencriptar |
| **Timestamp** | DateTime | Fecha y hora de creación |

---

## 🧪 Ejemplos de Pruebas

### Prueba 1: Validación de Campos Requeridos

**Falta `urlBC`:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"authType":"Basic","user":"usuario","pass":"pass","encryptData":"test"}'; $response.Content
```
**Respuesta esperada:** `{"error": "Missing field 'urlBC'"}`

### Prueba 2: Validación de authType

**authType inválido:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.com","authType":"Invalid","user":"usuario","pass":"pass","encryptData":"test"}'; $response.Content
```
**Respuesta esperada:** `{"error": "Invalid 'authType'. Must be 'Basic' or 'oAuth'"}`

### Prueba 3: Validación de encryptType

**encryptType inválido:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.com","authType":"Basic","user":"usuario","pass":"pass","encryptType":"MD5","encryptData":"test"}'; $response.Content
```
**Respuesta esperada:** `{"error": "Invalid 'encryptType'. Must be 'SHA-256' or 'SHA-512'"}`

---

## 📝 Notas Importantes

1. **Desarrollo Local:** La tabla se crea automáticamente en el emulador local (Azurite) cuando ejecutas `func start`
2. **Azure en la Nube:** La tabla se crea automáticamente cuando se ejecuta la función por primera vez en Azure
3. **Datos Sensibles:** Los campos `Pass` y `EncryptKey` contienen información sensible. Ten cuidado al compartir capturas de pantalla o logs
4. **ID Único:** Cada llamada genera un UUID único que se guarda en `Id` y `RowKey`. Este ID se usa después para buscar los datos cuando RedSys llama a `DecryptAndRedirect`

---

## 🐛 Solución de Problemas

### Error: "Table not found"
- **Causa:** La tabla aún no se ha creado
- **Solución:** Ejecuta la función al menos una vez para que se cree la tabla automáticamente

### Error: "Cannot connect to storage emulator"
- **Causa:** Azurite no está corriendo
- **Solución:** Asegúrate de que `func start` esté ejecutándose, o instala y ejecuta Azurite manualmente

### No veo datos en la tabla
- **Causa:** La función no se ejecutó correctamente o hubo un error
- **Solución:** 
  1. Verifica los logs de `func start`
  2. Verifica que la llamada HTTP devolvió status 200
  3. Revisa que el binding de Table Storage esté configurado correctamente en `function.json`

---

## 📚 Referencias

- [Azure Storage Explorer](https://azure.microsoft.com/features/storage-explorer/)
- [Azure Table Storage Documentation](https://docs.microsoft.com/azure/storage/tables/)
- [Azure Functions Python Documentation](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)


