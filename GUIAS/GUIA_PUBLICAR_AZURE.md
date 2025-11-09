# ☁️ Guía para Publicar en Azure

Esta guía explica cómo publicar la función `EncryptData` en Azure.

---

## 🚀 Opción 1: Publicar con Azure Functions Core Tools (Rápido)

### Prerrequisitos

1. **Azure CLI instalado y autenticado:**
```powershell
# Verificar si está instalado
az --version

# Si no está instalado, instálalo:
# Windows: https://aka.ms/installazurecliwindows
# O con PowerShell:
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; Remove-Item .\AzureCLI.msi

# Autenticarse
az login
```

2. **Azure Functions Core Tools instalado:**
```powershell
# Verificar
func --version

# Si no está instalado:
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

3. **Function App creada en Azure** (ver `GUIA_INSTALACION_CLIENTE.md` si no la tienes)

### Paso 1: Verificar que estás autenticado

```powershell
az account show
```

Si no estás autenticado o necesitas cambiar de suscripción:
```powershell
az login
az account list --output table
az account set --subscription "<SUBSCRIPTION-ID>"
```

### Paso 2: Publicar la Función

**Desde el directorio del proyecto:**

```powershell
# Reemplaza <nombre-function-app> con el nombre de tu Function App
func azure functionapp publish <nombre-function-app> --python
```

**Ejemplo:**
```powershell
func azure functionapp publish suitechredsys --python
```

### Paso 3: Verificar el Despliegue

Después de publicar, verás algo como:

```
Functions in suitechredsys:
    EncryptData - [httpTrigger]
        Invoke url: https://suitechredsys.azurewebsites.net/api/EncryptData
```

### Paso 4: Probar la Función en Azure

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

$response = Invoke-WebRequest -Uri "https://<nombre-function-app>.azurewebsites.net/api/EncryptData" -Method POST -ContentType "application/json" -Body $body
$response.Content
```

**Ejemplo con el nombre real:**
```powershell
$response = Invoke-WebRequest -Uri "https://suitechredsys.azurewebsites.net/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.example.com/api/endpoint","authType":"Basic","user":"usuario_bc","pass":"contraseña_bc","encryptType":"SHA-256","encryptKey":"clave_secreta","encryptData":"datos a encriptar"}'; $response.Content
```

---

## 🔄 Opción 2: Publicar con GitHub Actions (Automático)

Si ya tienes configurado GitHub Actions (archivo `.github/workflows/master_suitechredsys.yml`):

### Paso 1: Hacer Commit y Push

```powershell
# Verificar cambios
git status

# Agregar archivos
git add .

# Hacer commit
git commit -m "Actualizar función EncryptData con tabla de almacenamiento"

# Push a master
git push origin master
```

### Paso 2: Verificar el Despliegue

1. Ve a tu repositorio en GitHub
2. Haz clic en la pestaña **"Actions"**
3. Verás el workflow ejecutándose
4. Espera a que termine (2-5 minutos)
5. Si hay errores, revisa los logs

### Paso 3: Probar la Función

Una vez desplegado, prueba con la URL de Azure:
```powershell
$response = Invoke-WebRequest -Uri "https://suitechredsys.azurewebsites.net/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"urlBC":"https://bc.example.com/api/endpoint","authType":"Basic","user":"usuario_bc","pass":"contraseña_bc","encryptType":"SHA-256","encryptKey":"clave_secreta","encryptData":"datos a encriptar"}'; $response.Content
```

---

## 📊 Ver la Tabla en Azure

Una vez que hayas ejecutado la función en Azure:

### Opción 1: Azure Portal

1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca tu **Storage Account** (ej: `rgsuitechredsysa040`)
3. En el menú lateral, selecciona **"Tables"**
4. Busca **"EncryptDataLogs"**
5. Haz clic para ver las entidades (filas)

### Opción 2: Azure Storage Explorer

1. Abre **Azure Storage Explorer**
2. Conecta a tu cuenta de Azure (si no está conectada)
3. Expande tu suscripción → **Storage Accounts** → [Tu Storage Account] → **Tables**
4. Busca **"EncryptDataLogs"**
5. Haz clic derecho en **"Tables"** → **"Refresh"** si no aparece
6. Haz doble clic en la tabla para ver los datos

### Opción 3: Script Python (Actualizar Connection String)

Actualiza `consultar_tabla.py` con la connection string de Azure:

```python
# Obtener la connection string desde Azure Portal:
# Storage Account → Access Keys → Connection string

CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=<nombre>;AccountKey=<key>;EndpointSuffix=core.windows.net"
```

Luego ejecuta:
```powershell
python consultar_tabla.py
```

---

## 🐛 Solución de Problemas

### Error: "Function App not found"

**Solución:**
- Verifica que el nombre de la Function App sea correcto
- Verifica que estés en la suscripción correcta: `az account show`
- Verifica que la Function App exista: `az functionapp list --output table`

### Error: "Authentication failed"

**Solución:**
```powershell
# Re-autenticarse
az login

# Verificar suscripción
az account show
```

### Error: "Deployment failed"

**Solución:**
- Verifica que todos los archivos estén en el directorio correcto
- Verifica que `requirements.txt` tenga todas las dependencias
- Revisa los logs de despliegue para más detalles

### La tabla no aparece después del despliegue

**Solución:**
1. Ejecuta la función al menos una vez en Azure (la tabla se crea automáticamente)
2. Espera unos segundos
3. Refresca la vista en Azure Portal o Storage Explorer

---

## ✅ Checklist de Despliegue

- [ ] Azure CLI instalado y autenticado (`az login`)
- [ ] Azure Functions Core Tools instalado (`func --version`)
- [ ] Function App creada en Azure
- [ ] Estás en el directorio correcto del proyecto
- [ ] Todos los archivos están guardados
- [ ] `requirements.txt` está actualizado
- [ ] Ejecutaste `func azure functionapp publish <nombre> --python`
- [ ] El despliegue se completó sin errores
- [ ] Probaste la función en Azure
- [ ] La tabla `EncryptDataLogs` aparece en Azure Storage

---

## 📝 Notas Importantes

1. **Primera Ejecución:** La tabla `EncryptDataLogs` se crea automáticamente cuando ejecutas la función por primera vez en Azure
2. **Storage Account:** Asegúrate de que la Function App esté usando el Storage Account correcto
3. **URL de Producción:** La URL será: `https://<nombre-function-app>.azurewebsites.net/api/EncryptData`
4. **Logs:** Puedes ver los logs en Azure Portal → Function App → Functions → EncryptData → Monitor

---

## 🎯 Próximos Pasos

Después de publicar:

1. **Probar la función** con una llamada real
2. **Verificar la tabla** en Azure Storage
3. **Configurar monitoreo** en Azure Portal si es necesario
4. **Configurar autenticación** si es necesario (actualmente está en `anonymous`)


