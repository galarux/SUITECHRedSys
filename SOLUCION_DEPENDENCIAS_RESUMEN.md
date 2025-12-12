# 🔧 Solución al Problema de Dependencias - Resumen Ejecutivo

## 🚨 Problema Identificado

**Error recurrente:** `ModuleNotFoundError: No module named 'requests'`

**Causa raíz:** Azure Functions no estaba configurado para usar **Remote Build**, lo que causaba que las dependencias no se instalaran correctamente en Azure. Cuando el worker se reciclaba (por inactividad, actualizaciones, etc.), las dependencias desaparecían.

---

## ✅ Solución Implementada

Se han creado **4 archivos nuevos** y actualizado **3 archivos existentes** para resolver el problema permanentemente:

### 📁 Archivos Nuevos

1. **`deploy.ps1`** - Script de despliegue automático para Windows
   - Limpia archivos locales de Python
   - Configura Remote Build en Azure
   - Despliega con las flags correctas
   - Verifica que la función esté disponible

2. **`deploy.sh`** - Script de despliegue automático para Linux/Mac
   - Misma funcionalidad que `deploy.ps1`

3. **`.deployment`** - Configuración de despliegue de Azure
   - Fuerza Remote Build durante el despliegue

4. **`GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md`** - Guía completa
   - Explica el problema en detalle
   - Soluciones paso a paso
   - Checklist de verificación
   - Solución de emergencia

### 📝 Archivos Actualizados

1. **`.funcignore`** - Excluye archivos que no deben subirse
   - Añadidos: `.python_packages`, `__pycache__`, archivos de desarrollo

2. **`host.json`** - Configuración mejorada
   - Añadido: extensionBundle, logging, timeout

3. **`README.md`** - Documentación principal actualizada
   - Advertencia sobre Remote Build
   - Instrucciones de despliegue correctas

4. **`GUIAS/GUIA_PUBLICAR_AZURE.md`** - Guía de publicación actualizada
   - Instrucciones correctas con `--build remote`
   - Advertencias sobre errores comunes

---

## 🚀 Cómo Usar la Solución

### Despliegue Inmediato (Solución de Emergencia)

Si la función **ya está fallando en producción**, ejecuta:

**Windows:**
```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh suitechredsys
```

Esto:
1. ✅ Limpiará archivos locales problemáticos
2. ✅ Configurará Remote Build en Azure
3. ✅ Desplegará correctamente
4. ✅ Verificará que funcione

### Despliegues Futuros

**Siempre usa uno de estos métodos:**

**Opción 1 - Script automático (RECOMENDADO):**
```powershell
.\deploy.ps1
```

**Opción 2 - Manual con Remote Build:**
```bash
# Limpiar
rm -rf .python_packages __pycache__

# Desplegar
func azure functionapp publish suitechredsys --python --build remote
```

**❌ NUNCA hagas esto:**
```bash
# ❌ SIN --build remote
func azure functionapp publish suitechredsys --python
```

---

## 🔍 Verificación Post-Despliegue

### 1. Verificar Settings en Azure Portal

Ve a: **Function App → Configuration → Application settings**

Debe existir:
- `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
- `ENABLE_ORYX_BUILD` = `true`

### 2. Probar la función

```bash
curl -X POST https://suitechredsys.azurewebsites.net/api/PaygoldLink \
  -H "Content-Type: application/json" \
  -d '{"urlBC":"https://test.com","authType":"basic","user":"test","pass":"test","encryptData":{"DS_MERCHANT_ORDER":"TEST001","DS_MERCHANT_AMOUNT":"100"},"redirectURL":"https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST","encryptKey":"sq7HjrUOBfKmC576ILgskD5srU870gJ7"}'
```

Si recibes JSON (no error 500), ✅ está funcionando correctamente.

### 3. Monitorear logs

```bash
az functionapp log tail --name suitechredsys --resource-group <tu-resource-group>
```

No debe aparecer `ModuleNotFoundError`.

---

## 📚 Documentación Adicional

- **Guía completa:** `GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md`
- **Guía de publicación:** `GUIAS/GUIA_PUBLICAR_AZURE.md`
- **README principal:** `README.md`

---

## 🎯 Resultado Esperado

Después de aplicar esta solución:

✅ Las dependencias se instalan correctamente en Azure
✅ El problema NO volverá a ocurrir después de reinicios
✅ Los despliegues futuros serán consistentes
✅ Tienes scripts automáticos para desplegar sin errores

---

## 📞 Si el Problema Persiste

1. Ejecuta el script de despliegue: `.\deploy.ps1`
2. Verifica los logs: `az functionapp log tail --name suitechredsys`
3. Consulta: `GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md`
4. Verifica que Remote Build esté activo en Azure Portal

---

**Fecha de implementación:** 12/12/2025
**Estado:** ✅ Solución completa implementada

