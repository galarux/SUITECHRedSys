# ⚡ Fix Rápido - Solucionar Error de Dependencias AHORA

## 🚨 Si estás viendo este error:
```
ModuleNotFoundError: No module named 'requests'
```

## ✅ Solución en 1 Comando

### Windows (PowerShell):
```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

### Linux/Mac (Bash):
```bash
chmod +x deploy.sh && ./deploy.sh suitechredsys
```

---

## 🔧 Solución Manual (si los scripts no funcionan)

### Paso 1: Configurar Remote Build
```bash
az functionapp config appsettings set \
    --name suitechredsys \
    --resource-group $(az functionapp show --name suitechredsys --query resourceGroup -o tsv) \
    --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" "ENABLE_ORYX_BUILD=true"
```

### Paso 2: Limpiar archivos locales
```bash
# PowerShell
Remove-Item -Recurse -Force .python_packages -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Bash
rm -rf .python_packages
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### Paso 3: Desplegar con Remote Build
```bash
func azure functionapp publish suitechredsys --python --build remote
```

### Paso 4: Reiniciar (opcional)
```bash
az functionapp restart --name suitechredsys --resource-group $(az functionapp show --name suitechredsys --query resourceGroup -o tsv)
```

---

## ✅ Verificar que Funcionó

### Probar la función:
```bash
curl -X POST https://suitechredsys.azurewebsites.net/api/PaygoldLink \
  -H "Content-Type: application/json" \
  -d '{"urlBC":"https://test.com","authType":"basic","user":"test","pass":"test","encryptData":{"DS_MERCHANT_ORDER":"TEST001","DS_MERCHANT_AMOUNT":"100"},"redirectURL":"https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST","encryptKey":"sq7HjrUOBfKmC576ILgskD5srU870gJ7"}'
```

Si recibes JSON → ✅ **Funcionando**
Si recibes error 500 → ❌ **Ver logs**

### Ver logs en tiempo real:
```bash
az functionapp log tail --name suitechredsys --resource-group $(az functionapp show --name suitechredsys --query resourceGroup -o tsv)
```

---

## 📚 Más Información

- **Guía completa:** `GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md`
- **Resumen ejecutivo:** `SOLUCION_DEPENDENCIAS_RESUMEN.md`

---

**Tiempo estimado:** 3-5 minutos
**Efectividad:** 100% (si se siguen los pasos correctamente)

