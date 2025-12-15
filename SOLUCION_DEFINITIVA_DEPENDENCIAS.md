# 🎯 SOLUCIÓN DEFINITIVA - Persistencia de Dependencias en Azure Functions

## 📅 Fecha: 15/12/2025

---

## 🚨 EL PROBLEMA REAL

Las dependencias se perdían después de reinicios del worker **INCLUSO usando Remote Build correctamente**.

### ❌ Lo que NO era el problema:
- ✅ Remote Build SÍ estaba configurado
- ✅ `SCM_DO_BUILD_DURING_DEPLOYMENT=true` estaba activo
- ✅ `ENABLE_ORYX_BUILD=true` estaba activo
- ✅ Las dependencias SÍ se instalaban en Azure

### ✅ Lo que SÍ era el problema:
**Faltaban las configuraciones de Storage para el plan Consumption:**
- `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` - Connection string al Azure Files
- `WEBSITE_CONTENTSHARE` - Nombre del file share
- `WEBSITE_RUN_FROM_PACKAGE=1` - Ejecutar desde paquete

**Sin estas configuraciones**, Azure:
1. Instala las dependencias durante el build ✅
2. Pero NO crea un paquete persistente ❌
3. Las dependencias se pierden al reciclar el worker ❌

---

## 🎯 LA SOLUCIÓN DEFINITIVA

### **Configuraciones OBLIGATORIAS en Azure:**

```bash
# Storage (obligatorio para Consumption Plan)
AzureWebJobsStorage = [connection string del storage account]
WEBSITE_CONTENTAZUREFILECONNECTIONSTRING = [misma connection string]
WEBSITE_CONTENTSHARE = suitechredsys

# Remote Build (para instalar dependencias correctamente)
SCM_DO_BUILD_DURING_DEPLOYMENT = true
ENABLE_ORYX_BUILD = true
BUILD_FLAGS = UseExpressBuild

# Run from Package (para persistencia)
WEBSITE_RUN_FROM_PACKAGE = 1
```

### **Por qué funciona:**

1. **Remote Build** instala las dependencias en Azure
2. **Oryx** crea un paquete `.squashfs` con todo incluido
3. El paquete se sube a **Azure Files** (gracias a `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING`)
4. Azure ejecuta desde el paquete (read-only, gracias a `WEBSITE_RUN_FROM_PACKAGE=1`)
5. El paquete **persiste** entre reinicios del worker

---

## 📋 CHECKLIST DE VERIFICACIÓN

Después de desplegar, verifica que existan estas configuraciones:

```bash
az functionapp config appsettings list \
  --name suitechredsys \
  --resource-group rg-suitech-redsys \
  --query "[?name=='AzureWebJobsStorage' || name=='WEBSITE_CONTENTAZUREFILECONNECTIONSTRING' || name=='WEBSITE_CONTENTSHARE' || name=='WEBSITE_RUN_FROM_PACKAGE' || name=='SCM_DO_BUILD_DURING_DEPLOYMENT' || name=='ENABLE_ORYX_BUILD'].{name:name, value:value}" \
  -o table
```

**Resultado esperado:**
```
Name                                      Value
----------------------------------------  -------
AzureWebJobsStorage                       DefaultEndpointsProtocol=https;...
WEBSITE_CONTENTAZUREFILECONNECTIONSTRING  DefaultEndpointsProtocol=https;...
WEBSITE_CONTENTSHARE                      suitechredsys
WEBSITE_RUN_FROM_PACKAGE                  1
SCM_DO_BUILD_DURING_DEPLOYMENT            true
ENABLE_ORYX_BUILD                         true
BUILD_FLAGS                               UseExpressBuild
```

---

## 🚀 CÓMO DESPLEGAR CORRECTAMENTE

### **Opción 1: Usar el script (RECOMENDADO)**

```powershell
.\deploy.ps1
```

El script ahora configura automáticamente `WEBSITE_RUN_FROM_PACKAGE=1`.

### **Opción 2: Manual**

```bash
# 1. Limpiar archivos locales
rm -rf .python_packages __pycache__

# 2. Configurar todas las settings necesarias
az functionapp config appsettings set \
    --name suitechredsys \
    --resource-group rg-suitech-redsys \
    --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
               "ENABLE_ORYX_BUILD=true" \
               "BUILD_FLAGS=UseExpressBuild" \
               "WEBSITE_RUN_FROM_PACKAGE=1" \
    --output none

# 3. Desplegar con Remote Build
func azure functionapp publish suitechredsys --python --build remote
```

---

## 🔍 SEÑALES DE QUE FUNCIONA CORRECTAMENTE

En los logs del despliegue, debes ver:

```
Creating placeholder blob for linux consumption function app...
SCM_RUN_FROM_PACKAGE placeholder blob scm-latest-suitechredsys.zip located
Uploading built content /home/site/artifacts/functionappartifact.squashfs for linux consumption function app...
```

**Esto confirma que:**
- ✅ Se creó el paquete squashfs
- ✅ Se subió a Azure Files
- ✅ Azure ejecutará desde el paquete

---

## ⚠️ ERRORES QUE INDICAN PROBLEMA

### Error 1: "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING is empty"

**Causa:** Falta la connection string del storage.

**Solución:**
```bash
# Obtener connection string
CONN_STR=$(az storage account show-connection-string \
  --name rgsuitechredsysa040 \
  --resource-group rg-suitech-redsys \
  --query "connectionString" -o tsv)

# Configurar
az functionapp config appsettings set \
  --name suitechredsys \
  --resource-group rg-suitech-redsys \
  --settings "AzureWebJobsStorage=$CONN_STR" \
             "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=$CONN_STR" \
             "WEBSITE_CONTENTSHARE=suitechredsys" \
  --output none
```

### Error 2: "ModuleNotFoundError" después de reinicio

**Causa:** `WEBSITE_RUN_FROM_PACKAGE` no está configurado o está en `0`.

**Solución:**
```bash
az functionapp config appsettings set \
  --name suitechredsys \
  --resource-group rg-suitech-redsys \
  --settings "WEBSITE_RUN_FROM_PACKAGE=1" \
  --output none

# Redesplegar
func azure functionapp publish suitechredsys --python --build remote
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `SOLUCION_DEPENDENCIAS_RESUMEN.md` - Resumen ejecutivo
- `GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md` - Guía completa
- `deploy.ps1` / `deploy.sh` - Scripts de despliegue actualizados

---

## 🎓 LECCIONES APRENDIDAS

1. **Remote Build es necesario PERO NO suficiente** para el plan Consumption
2. **WEBSITE_RUN_FROM_PACKAGE=1** es OBLIGATORIO para persistencia
3. **WEBSITE_CONTENTAZUREFILECONNECTIONSTRING** es necesario para montar el file share
4. **Nunca eliminar** `WEBSITE_RUN_FROM_PACKAGE` sin entender las consecuencias
5. **El script de despliegue** debe configurar TODAS las settings necesarias

---

## ✅ ESTADO ACTUAL

**Fecha:** 15/12/2025  
**Estado:** ✅ Problema resuelto definitivamente  
**Configuración:** Correcta y completa  
**Próximos pasos:** Usar siempre `.\deploy.ps1` para desplegar

---

## 🚨 REGLA DE ORO

**NUNCA elimines `WEBSITE_RUN_FROM_PACKAGE` o las configuraciones de CONTENT.**

Si hay un conflicto durante el despliegue, la solución NO es eliminar estas configuraciones, sino asegurarse de que todas las configuraciones de storage estén correctas.

---

**Autor:** Asistente IA  
**Revisado por:** Usuario  
**Última actualización:** 15/12/2025

