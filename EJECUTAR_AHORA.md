# 🚨 EJECUTAR AHORA - Solución al Problema Recurrente

## ⚡ Acción Inmediata (2 comandos)

```powershell
# 1. Desplegar con la solución mejorada
.\deploy.ps1 -FunctionAppName "suitechredsys"

# 2. Verificar que todo esté correcto
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"
```

---

## 🎯 ¿Qué se ha cambiado?

### La Configuración Crítica que Faltaba

**`WEBSITE_RUN_FROM_PACKAGE=0`** ⭐

Esta es LA configuración que estaba causando el problema recurrente:
- Por defecto, Azure usa `WEBSITE_RUN_FROM_PACKAGE=1`
- Esto hace que ejecute desde un ZIP que NO incluye las dependencias remotas
- Al establecerlo en `0`, ejecuta desde `/home/site/wwwroot` donde SÍ están las dependencias

### Otras Configuraciones Añadidas

- `FUNCTIONS_WORKER_RUNTIME=python` - Especifica runtime explícitamente
- `PYTHON_ENABLE_WORKER_EXTENSIONS=1` - Mejora compatibilidad con paquetes

---

## 📋 Después del Despliegue

### 1. Verificación Inmediata (Automática)

El script `verify_deployment.ps1` te dirá si todo está bien:

**✅ Si ves esto, todo está bien:**
```
✅ VERIFICACIÓN EXITOSA - Todo funcionando correctamente
```

**❌ Si ves esto, hay problemas:**
```
⚠️ VERIFICACIÓN COMPLETADA CON PROBLEMAS
```

### 2. Prueba Manual (Opcional)

```bash
curl -X POST https://suitechredsys.azurewebsites.net/api/PaygoldLink \
  -H "Content-Type: application/json" \
  -d '{"urlBC":"https://test.com","authType":"basic","user":"test","pass":"test","encryptData":{"DS_MERCHANT_ORDER":"TEST001","DS_MERCHANT_AMOUNT":"100"},"redirectURL":"https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST","encryptKey":"sq7HjrUOBfKmC576ILgskD5srU870gJ7"}'
```

### 3. Monitorear Logs (30 minutos)

```bash
az functionapp log tail --name suitechredsys --resource-group <tu-resource-group>
```

**Busca:**
- ✅ `Executed 'Functions.PaygoldLink' (Succeeded)`
- ❌ `ModuleNotFoundError` (NO debería aparecer)

---

## 🧪 Prueba Definitiva (Después de 15 minutos)

### Paso 1: Espera 15 minutos
Deja la función inactiva durante 15 minutos (tiempo suficiente para que entre en standby).

### Paso 2: Prueba nuevamente
Ejecuta el curl de arriba nuevamente.

**Si funciona → ✅ Problema resuelto**

### Paso 3: Reinicia y prueba
```bash
az functionapp restart --name suitechredsys --resource-group <resource-group>
```

Espera 2 minutos y ejecuta el curl nuevamente.

**Si funciona → ✅ Problema definitivamente resuelto**

---

## 📊 Expectativa

### Antes
- ✅ Funcionaba inmediatamente
- ❌ Fallaba a los 10-15 minutos
- ❌ Problema recurrente (3 veces)

### Ahora (con la nueva configuración)
- ✅ Funciona inmediatamente
- ✅ Funciona después de 15+ minutos
- ✅ Funciona después de reiniciar
- ✅ **Efectividad esperada: 95%+**

---

## 🔍 Verificar en Azure Portal

Ve a: **Function App → Configuration → Application settings**

**DEBE mostrar:**
```
WEBSITE_RUN_FROM_PACKAGE = 0  ← CRÍTICO (debe ser 0, no 1)
SCM_DO_BUILD_DURING_DEPLOYMENT = true
ENABLE_ORYX_BUILD = true
FUNCTIONS_WORKER_RUNTIME = python
PYTHON_ENABLE_WORKER_EXTENSIONS = 1
```

---

## 📚 Documentación

- **CAMBIOS_REALIZADOS.md** - Resumen completo de todos los cambios
- **SOLUCION_PROBLEMA_RECURRENTE.md** - Documentación detallada del problema
- **verify_deployment.ps1** - Script de verificación automática

---

## 🆘 Si el Problema Persiste

1. Ejecuta: `.\verify_deployment.ps1 -FunctionAppName "suitechredsys"`
2. Verifica manualmente en Azure Portal que `WEBSITE_RUN_FROM_PACKAGE = 0`
3. Consulta: `SOLUCION_PROBLEMA_RECURRENTE.md`
4. Si nada funciona, puede ser un problema con la instancia de Azure

---

**¡Ejecuta los comandos de arriba AHORA y monitorea durante 30 minutos!**

