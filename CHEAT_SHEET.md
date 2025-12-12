# 🚀 Cheat Sheet - SUITECH RedSys Functions

Referencia rápida de comandos y configuraciones más importantes.

---

## ⚡ Comandos Esenciales

### Desplegar (SIEMPRE usar esto)
```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

### Verificar Despliegue
```powershell
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"
```

### Ver Logs en Tiempo Real
```bash
az functionapp log tail --name suitechredsys --resource-group rg-suitech-redsys
```

### Reiniciar Function App
```bash
az functionapp restart --name suitechredsys --resource-group rg-suitech-redsys
```

---

## 🔧 Configuraciones Críticas

### Verificar Configuración
```bash
az functionapp config appsettings list \
    --name suitechredsys \
    --resource-group rg-suitech-redsys \
    --query "[?name=='WEBSITE_RUN_FROM_PACKAGE' || name=='SCM_DO_BUILD_DURING_DEPLOYMENT' || name=='ENABLE_ORYX_BUILD'].{name:name, value:value}" \
    -o table
```

### Configuración Correcta (Debe Mostrar)
```
WEBSITE_RUN_FROM_PACKAGE = 0              ⭐ CRÍTICO
SCM_DO_BUILD_DURING_DEPLOYMENT = true
ENABLE_ORYX_BUILD = true
```

### Establecer Configuración Manualmente (Si Falta)
```bash
az functionapp config appsettings set \
    --name suitechredsys \
    --resource-group rg-suitech-redsys \
    --settings \
        "WEBSITE_RUN_FROM_PACKAGE=0" \
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
        "ENABLE_ORYX_BUILD=true" \
        "FUNCTIONS_WORKER_RUNTIME=python" \
        "PYTHON_ENABLE_WORKER_EXTENSIONS=1"
```

---

## 🧪 Probar Endpoints

### Con PowerShell
```powershell
$body = '{"urlBC":"https://test.com","authType":"basic","user":"test","pass":"test","encryptData":{"DS_MERCHANT_ORDER":"TEST001","DS_MERCHANT_AMOUNT":"100"},"redirectURL":"https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST","encryptKey":"sq7HjrUOBfKmC576ILgskD5srU870gJ7"}'

Invoke-WebRequest -Uri "https://suitechredsys.azurewebsites.net/api/paygoldlink" -Method POST -Body $body -ContentType "application/json"
```

### Con curl
```bash
curl -X POST https://suitechredsys.azurewebsites.net/api/paygoldlink \
  -H "Content-Type: application/json" \
  -d '{"urlBC":"https://test.com","authType":"basic","user":"test","pass":"test","encryptData":{"DS_MERCHANT_ORDER":"TEST001","DS_MERCHANT_AMOUNT":"100"},"redirectURL":"https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST","encryptKey":"sq7HjrUOBfKmC576ILgskD5srU870gJ7"}'
```

### Con Postman
```
POST https://suitechredsys.azurewebsites.net/api/paygoldlink?code={{paygold_funcKey}}
Content-Type: application/json

{
  "urlBC": "https://api.businesscentral.dynamics.com/...",
  "authType": "oAuth",
  "user": "{{client_id_oauth}}",
  "pass": "{{client_secret_oauth}}",
  "encryptData": {
    "DS_MERCHANT_ORDER": "TEST001",
    "DS_MERCHANT_AMOUNT": "100",
    "DS_MERCHANT_CURRENCY": "978",
    "DS_MERCHANT_MERCHANTCODE": "263100000",
    "DS_MERCHANT_TERMINAL": "49",
    "DS_MERCHANT_TRANSACTIONTYPE": "0"
  },
  "redirectURL": "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST",
  "encryptKey": "sq7HjrUOBfKmC576ILgskD5srU870gJ7"
}
```

---

## 🔍 Diagnóstico

### Ver Estado de la Function App
```bash
az functionapp show --name suitechredsys --resource-group rg-suitech-redsys --query "{state:state, availabilityState:availabilityState}" -o table
```

### Listar Funciones Disponibles
```bash
az functionapp function list --name suitechredsys --resource-group rg-suitech-redsys --query "[].{name:name, invokeUrlTemplate:invokeUrlTemplate}" -o table
```

### Sincronizar Triggers
```bash
az rest --method POST --uri "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-suitech-redsys/providers/Microsoft.Web/sites/suitechredsys/syncfunctiontriggers?api-version=2022-03-01"
```

---

## 📊 Códigos de Respuesta

| Código | Significado | Acción |
|--------|-------------|--------|
| 200 | ✅ Éxito | Todo bien |
| 401 | ✅ Función viva (requiere auth) | Normal, añade `?code=...` |
| 404 | ⚠️ Función no encontrada | Espera 1-2 min o re-despliega |
| 500 | ❌ Error interno | Verificar logs (puede ser ModuleNotFoundError) |

---

## 🚨 Solución de Problemas

### Si aparece `ModuleNotFoundError`

1. **Re-desplegar:**
   ```powershell
   .\deploy.ps1 -FunctionAppName "suitechredsys"
   ```

2. **Verificar configuración:**
   ```bash
   az functionapp config appsettings list --name suitechredsys --resource-group rg-suitech-redsys --query "[?name=='WEBSITE_RUN_FROM_PACKAGE'].{name:name, value:value}" -o table
   ```
   
   **Debe ser:** `WEBSITE_RUN_FROM_PACKAGE = 0`

3. **Ver documentación completa:**
   - [`PROBLEMA_RESUELTO.md`](PROBLEMA_RESUELTO.md)

### Si el endpoint da 404

1. **Espera 1-2 minutos** (la función puede estar inicializándose)

2. **Sincroniza triggers:**
   ```bash
   az rest --method POST --uri "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-suitech-redsys/providers/Microsoft.Web/sites/suitechredsys/syncfunctiontriggers?api-version=2022-03-01"
   ```

3. **Reinicia:**
   ```bash
   az functionapp restart --name suitechredsys --resource-group rg-suitech-redsys
   ```

---

## 📁 Estructura de URLs

### Endpoints Disponibles

```
https://suitechredsys.azurewebsites.net/api/paygoldlink
https://suitechredsys.azurewebsites.net/api/decryptandredirect
```

**Nota:** URLs en minúsculas (Azure Functions en Linux es case-sensitive).

### Con Autenticación

```
https://suitechredsys.azurewebsites.net/api/paygoldlink?code=FUNCTION_KEY
https://suitechredsys.azurewebsites.net/api/decryptandredirect?code=FUNCTION_KEY
```

---

## 🔐 Variables de Entorno Requeridas

### En Azure (Application Settings)

```bash
AzureWebJobsStorage                    # Connection string de Storage Account
REDSYS_SHA256_KEY                      # Clave SHA256 de RedSys
REDSYS_MERCHANT_CODE                   # Código de comercio
REDSYS_TERMINAL                        # Terminal
REDSYS_REST_URL                        # URL del servicio RedSys
REDSYS_NOTIFICATION_URL                # URL de notificaciones (opcional)

# Configuraciones críticas (automáticas con deploy.ps1)
WEBSITE_RUN_FROM_PACKAGE=0             # ⭐ CRÍTICO
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
FUNCTIONS_WORKER_RUNTIME=python
PYTHON_ENABLE_WORKER_EXTENSIONS=1
```

---

## 📚 Documentación Rápida

| Necesito... | Documento |
|-------------|-----------|
| Solucionar `ModuleNotFoundError` | [`PROBLEMA_RESUELTO.md`](PROBLEMA_RESUELTO.md) |
| Acción inmediata | [`EJECUTAR_AHORA.md`](EJECUTAR_AHORA.md) |
| Resumen en una página | [`RESUMEN_EJECUTIVO.md`](RESUMEN_EJECUTIVO.md) |
| Índice completo | [`DOCUMENTACION_INDICE.md`](DOCUMENTACION_INDICE.md) |
| Documentación principal | [`README.md`](README.md) |

---

## ⚙️ Ejecución Local

### Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Configurar Local Settings
Edita `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "REDSYS_SHA256_KEY": "tu_clave_aqui",
    "REDSYS_MERCHANT_CODE": "263100000",
    "REDSYS_TERMINAL": "49",
    "REDSYS_REST_URL": "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST"
  }
}
```

### Iniciar Localmente
```bash
func start
```

### Endpoints Locales
```
http://localhost:7071/api/paygoldlink
http://localhost:7071/api/decryptandredirect
```

---

## 🎯 Checklist de Despliegue

- [ ] Ejecutar `.\deploy.ps1 -FunctionAppName "suitechredsys"`
- [ ] Ejecutar `.\verify_deployment.ps1 -FunctionAppName "suitechredsys"`
- [ ] Verificar que `WEBSITE_RUN_FROM_PACKAGE=0`
- [ ] Probar endpoint inmediatamente
- [ ] Esperar 15 minutos y probar nuevamente
- [ ] Reiniciar y probar (prueba crítica)
- [ ] Monitorear logs durante 30 minutos

---

## 🏆 Comandos Más Usados

```powershell
# Desplegar
.\deploy.ps1 -FunctionAppName "suitechredsys"

# Verificar
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"

# Ver logs
az functionapp log tail --name suitechredsys --resource-group rg-suitech-redsys

# Reiniciar
az functionapp restart --name suitechredsys --resource-group rg-suitech-redsys

# Ver configuración
az functionapp config appsettings list --name suitechredsys --resource-group rg-suitech-redsys -o table
```

---

**Última actualización:** 12 de diciembre de 2025  
**Estado:** ✅ Problema resuelto y documentado

