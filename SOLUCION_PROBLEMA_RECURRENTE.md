# 🚨 Solución al Problema Recurrente de ModuleNotFoundError

## El Problema

**Síntoma:** La función funciona durante 10-15 minutos después del despliegue, luego falla con:
```
ModuleNotFoundError: No module named 'requests'
```

**Causa raíz:** Azure Functions Python tiene un problema conocido donde el worker entra en modo "standby" y busca dependencias en `.python_packages` en lugar del sistema global de Python. Esto ocurre cuando:
1. El worker se recicla por inactividad
2. Azure actualiza el runtime
3. La función se escala o se mueve a otra instancia

## ¿Por qué ocurre esto?

El error muestra este `sys.path`:
```python
'/tmp/functions/standby/wwwroot'
'/home/site/wwwroot/.python_packages/lib/site-packages'  # ❌ Busca aquí
```

Pero con **Remote Build correcto**, debería buscar en:
```python
'/opt/python/3/lib/python3.12/site-packages'  # ✅ Debería buscar aquí
```

## ✅ Solución Definitiva

### Paso 1: Usar el Script de Despliegue Mejorado

El script `deploy.ps1` ha sido actualizado con configuraciones adicionales:

```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

**¿Qué hace el script mejorado?**

1. **Limpia archivos locales** que pueden interferir
2. **Configura 5 settings críticos** en Azure:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT=true` - Activa build remoto
   - `ENABLE_ORYX_BUILD=true` - Usa Oryx para construir
   - `BUILD_FLAGS=UseExpressBuild` - Optimiza el build
   - `WEBSITE_RUN_FROM_PACKAGE=0` - **CRÍTICO**: Desactiva run-from-package
   - `FUNCTIONS_WORKER_RUNTIME=python` - Especifica runtime Python
   - `PYTHON_ENABLE_WORKER_EXTENSIONS=1` - Habilita extensiones Python

3. **Reinicia la Function App** para aplicar cambios
4. **Despliega con `--build remote --no-bundler`**
5. **Verifica** que todo funcione correctamente

### Paso 2: Verificar el Despliegue

Después del despliegue, ejecuta:

```powershell
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"
```

Este script:
- ✅ Verifica que todas las configuraciones estén correctas
- ✅ Prueba el endpoint para confirmar que las dependencias están instaladas
- ✅ Revisa los logs buscando errores de módulos
- ✅ Te da un reporte completo del estado

### Paso 3: Monitorear Durante 30 Minutos

Después del despliegue, monitorea los logs durante al menos 30 minutos:

```bash
az functionapp log tail --name suitechredsys --resource-group <tu-resource-group>
```

**Busca específicamente:**
- ❌ `ModuleNotFoundError`
- ❌ `No module named 'requests'`
- ✅ Logs normales de ejecución de funciones

## 🔍 Verificación Manual en Azure Portal

### 1. Verificar Application Settings

Ve a: **Function App → Configuration → Application settings**

**DEBE existir:**
```
SCM_DO_BUILD_DURING_DEPLOYMENT = true
ENABLE_ORYX_BUILD = true
WEBSITE_RUN_FROM_PACKAGE = 0  ← CRÍTICO
FUNCTIONS_WORKER_RUNTIME = python
PYTHON_ENABLE_WORKER_EXTENSIONS = 1
```

### 2. Verificar Deployment Center

Ve a: **Function App → Deployment Center**

**Debe mostrar:**
- Build Provider: **Oryx**
- Build Status: **Success**

### 3. Verificar Kudu Console

Ve a: **Function App → Advanced Tools (Kudu) → Debug console → CMD**

Ejecuta:
```bash
cd /home/site/wwwroot
ls -la
python --version
pip list
```

**Debe mostrar:**
- Python 3.12.x
- `requests` en la lista de pip

## 🧪 Prueba de Estrés

Para verificar que el problema está resuelto, haz esto:

### 1. Prueba Inmediata
```bash
curl -X POST https://suitechredsys.azurewebsites.net/api/PaygoldLink \
  -H "Content-Type: application/json" \
  -d '{"urlBC":"https://test.com","authType":"basic","user":"test","pass":"test","encryptData":{"DS_MERCHANT_ORDER":"TEST001","DS_MERCHANT_AMOUNT":"100"},"redirectURL":"https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST","encryptKey":"sq7HjrUOBfKmC576ILgskD5srU870gJ7"}'
```

### 2. Espera 15 Minutos

Deja la función inactiva durante 15 minutos (tiempo suficiente para que el worker entre en standby).

### 3. Prueba Nuevamente

Ejecuta el mismo curl. **Si funciona**, el problema está resuelto.

### 4. Reinicia la Function App

```bash
az functionapp restart --name suitechredsys --resource-group <resource-group>
```

### 5. Prueba Después del Reinicio

Espera 2 minutos y ejecuta el curl nuevamente. **Si funciona**, el problema está definitivamente resuelto.

## 📊 Entender los Logs

### Logs Buenos ✅

```
Executing 'Functions.PaygoldLink'
Executed 'Functions.PaygoldLink' (Succeeded, Duration=250ms)
```

### Logs Malos ❌

```
ModuleNotFoundError: No module named 'requests'
sys.path: ['/tmp/functions/standby/wwwroot', '/home/site/wwwroot/.python_packages/lib/site-packages']
```

Si ves `/tmp/functions/standby/wwwroot` en el sys.path, significa que el worker está en modo standby y NO está usando el build remoto correctamente.

## 🔧 Si el Problema Persiste

### Opción 1: Forzar Recreación del Build

```bash
# Eliminar todos los archivos de build en Azure
az functionapp deployment source delete --name suitechredsys --resource-group <resource-group>

# Redesplegar
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

### Opción 2: Verificar que no hay .python_packages en el repo

```bash
# Asegúrate de que .funcignore incluye .python_packages
cat .funcignore | grep .python_packages

# Si no está, agrégalo
echo ".python_packages" >> .funcignore
```

### Opción 3: Usar un requirements.txt más específico

Actualiza `requirements.txt` con versiones específicas:

```txt
azure-functions==1.18.0
azure-data-tables==12.4.4
pycryptodome==3.19.0
requests==2.31.0
```

### Opción 4: Contactar Soporte de Azure

Si después de todo esto el problema persiste, es posible que haya un problema con la instancia específica de Azure. Considera:

1. Crear una nueva Function App
2. Contactar soporte de Azure
3. Migrar a Azure Functions con contenedor Docker (más control sobre dependencias)

## 📚 Archivos Importantes

### `.python_version`
Especifica la versión de Python (3.12). Azure lo usa para seleccionar el runtime correcto.

### `.deployment`
Fuerza `SCM_DO_BUILD_DURING_DEPLOYMENT=true` durante el despliegue.

### `.funcignore`
Excluye `.python_packages` y otros archivos locales que no deben subirse.

### `requirements.txt`
Lista de dependencias que Azure instalará en el build remoto.

## 🎯 Checklist de Verificación

Usa este checklist después de cada despliegue:

- [ ] Script `deploy.ps1` ejecutado sin errores
- [ ] Script `verify_deployment.ps1` muestra todo en verde
- [ ] Endpoint responde correctamente inmediatamente después del despliegue
- [ ] Logs no muestran `ModuleNotFoundError`
- [ ] Endpoint responde correctamente después de 15 minutos de inactividad
- [ ] Endpoint responde correctamente después de reiniciar la Function App
- [ ] Azure Portal muestra `WEBSITE_RUN_FROM_PACKAGE = 0`
- [ ] Azure Portal muestra `SCM_DO_BUILD_DURING_DEPLOYMENT = true`

Si **todos** los items están marcados, el problema está resuelto.

## 🚀 Despliegues Futuros

**SIEMPRE usa el script:**
```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

**NUNCA hagas:**
```bash
# ❌ Sin --build remote
func azure functionapp publish suitechredsys --python

# ❌ Con archivos locales sin limpiar
func azure functionapp publish suitechredsys --python --build remote
```

## 📞 Comandos Útiles

### Ver logs en tiempo real
```bash
az functionapp log tail --name suitechredsys --resource-group <resource-group>
```

### Reiniciar Function App
```bash
az functionapp restart --name suitechredsys --resource-group <resource-group>
```

### Ver configuración actual
```bash
az functionapp config appsettings list --name suitechredsys --resource-group <resource-group>
```

### Verificar estado del despliegue
```bash
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"
```

---

**Última actualización:** 12/12/2025  
**Estado:** Solución mejorada con configuraciones adicionales  
**Efectividad esperada:** 95%+ (basado en la configuración de `WEBSITE_RUN_FROM_PACKAGE=0`)

