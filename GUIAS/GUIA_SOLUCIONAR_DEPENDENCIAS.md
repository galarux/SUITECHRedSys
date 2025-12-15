# Guía: Solucionar Problemas de Dependencias en Azure Functions

## 🚨 Problema: "ModuleNotFoundError: No module named 'requests'"

Este error aparece cuando Azure Functions no puede encontrar las dependencias de Python, aunque estén en `requirements.txt`.

### ¿Por qué ocurre?

Azure Functions **recicla los workers** periódicamente por:
- Inactividad (cold start después de varios días)
- Actualizaciones de plataforma
- Cambios en configuración
- Optimización de recursos

Si las dependencias no se instalaron correctamente durante el despliegue, el error aparecerá al reiniciar.

---

## ✅ Solución Definitiva

### 1. Usar Remote Build (OBLIGATORIO)

Azure debe **compilar las dependencias en la nube**, no en tu máquina local.

#### Opción A: Usar el script de despliegue automático

**Windows (PowerShell):**
```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

**Linux/Mac (Bash):**
```bash
chmod +x deploy.sh
./deploy.sh suitechredsys
```

Estos scripts:
- ✅ Limpian archivos locales de Python
- ✅ Configuran Remote Build automáticamente
- ✅ Despliegan con las flags correctas
- ✅ Verifican que la función esté disponible

#### Opción B: Despliegue manual con Remote Build

```bash
# 1. Limpiar archivos locales
rm -rf .python_packages
find . -type d -name "__pycache__" -exec rm -rf {} +

# 2. Configurar Remote Build en Azure
az functionapp config appsettings set \
    --name suitechredsys \
    --resource-group <tu-resource-group> \
    --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
               "ENABLE_ORYX_BUILD=true" \
               "BUILD_FLAGS=UseExpressBuild"

# 3. Desplegar con Remote Build
func azure functionapp publish suitechredsys --python --build remote
```

---

## 🔍 Verificar que Remote Build está activo

### En Azure Portal:

1. Ve a tu Function App → **Configuration** → **Application settings**
2. Verifica que existan estas variables:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `ENABLE_ORYX_BUILD` = `true`
   - `BUILD_FLAGS` = `UseExpressBuild`

### Desde Azure CLI:

```bash
az functionapp config appsettings list \
    --name suitechredsys \
    --resource-group <tu-resource-group> \
    --query "[?name=='SCM_DO_BUILD_DURING_DEPLOYMENT' || name=='ENABLE_ORYX_BUILD'].{name:name, value:value}" \
    -o table
```

---

## 🛠️ Solución de Emergencia (Si el error ya ocurrió)

Si la función ya está fallando en producción:

### 1. Re-desplegar con Remote Build

```bash
# Usar el script automático (recomendado)
.\deploy.ps1

# O manualmente
func azure functionapp publish suitechredsys --python --build remote
```

### 2. Reiniciar la Function App

```bash
az functionapp restart --name suitechredsys --resource-group <tu-resource-group>
```

### 3. Verificar logs en tiempo real

```bash
az functionapp log tail --name suitechredsys --resource-group <tu-resource-group>
```

---

## 📋 Checklist Post-Despliegue

Después de cada despliegue, verifica:

- [ ] La función responde sin errores de módulos
- [ ] Los logs no muestran `ModuleNotFoundError`
- [ ] Las settings de Remote Build están configuradas
- [ ] El archivo `.funcignore` excluye `.python_packages`

### Prueba rápida con curl:

```bash
# Probar PaygoldLink
curl -X POST https://suitechredsys.azurewebsites.net/api/PaygoldLink \
  -H "Content-Type: application/json" \
  -d '{
    "urlBC": "https://test.com",
    "authType": "basic",
    "user": "test",
    "pass": "test",
    "encryptData": {
      "DS_MERCHANT_ORDER": "TEST001",
      "DS_MERCHANT_AMOUNT": "100"
    },
    "redirectURL": "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST",
    "encryptKey": "sq7HjrUOBfKmC576ILgskD5srU870gJ7"
  }'
```

Si recibes una respuesta JSON (no un error 500), las dependencias están correctamente instaladas.

---

## 🔧 Archivos Importantes

### `.funcignore`
Asegúrate de que excluye los paquetes locales:
```
.python_packages
__pycache__
*.pyc
.venv
```

### `.deployment`
Debe contener:
```
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### `requirements.txt`
Debe listar todas las dependencias:
```
azure-functions
azure-data-tables
pycryptodome
requests
```

---

## 🚫 Errores Comunes

### ❌ NO hacer esto:

```bash
# ❌ Desplegar SIN --build remote
func azure functionapp publish suitechredsys --python

# ❌ Subir .python_packages local
# (debe estar en .funcignore)

# ❌ Usar versiones de Python diferentes entre local y Azure
```

### ✅ Hacer esto:

```bash
# ✅ SIEMPRE usar --build remote
func azure functionapp publish suitechredsys --python --build remote

# ✅ Limpiar archivos locales antes de desplegar
rm -rf .python_packages __pycache__

# ✅ Usar Python 3.12 (o la versión configurada en Azure)
```

---

## 📞 Soporte Adicional

Si el problema persiste:

1. **Ver logs detallados del build:**
   ```bash
   az functionapp deployment source config-zip --name suitechredsys \
       --resource-group <tu-resource-group> \
       --src <path-to-zip> \
       --verbose
   ```

2. **Verificar la versión de Python en Azure:**
   ```bash
   az functionapp config show --name suitechredsys \
       --resource-group <tu-resource-group> \
       --query "linuxFxVersion"
   ```

3. **Revisar el Kudu console:**
   - Ve a: `https://suitechredsys.scm.azurewebsites.net`
   - Navega a `/home/site/wwwroot/.python_packages/lib/site-packages`
   - Verifica que `requests` esté instalado

---

## 📚 Referencias

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Remote Build Documentation](https://docs.microsoft.com/azure/azure-functions/functions-deployment-technologies#remote-build)
- [Troubleshooting Module Not Found](https://aka.ms/functions-modulenotfound)




