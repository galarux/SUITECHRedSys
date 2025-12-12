# 📚 Índice de Documentación - SUITECH RedSys Functions

Esta es la guía completa de toda la documentación del proyecto.

---

## 🚨 Documentos Críticos (Lee Primero)

### 1. [`PROBLEMA_RESUELTO.md`](PROBLEMA_RESUELTO.md) ⭐ **MÁS IMPORTANTE**
**¿Cuándo leer?** Si experimentas `ModuleNotFoundError` recurrente.

**Contenido:**
- ✅ Análisis completo del problema recurrente
- ✅ Solución definitiva implementada y verificada
- ✅ Pruebas realizadas (incluyendo reinicio exitoso)
- ✅ Configuraciones críticas explicadas
- ✅ Comandos útiles
- ✅ Checklist de verificación

**Estado:** ✅ Problema resuelto y documentado (12/12/2025)

---

### 2. [`EJECUTAR_AHORA.md`](EJECUTAR_AHORA.md) ⚡
**¿Cuándo leer?** Si la función está fallando AHORA y necesitas una solución inmediata.

**Contenido:**
- ⚡ 2 comandos para solucionar el problema inmediatamente
- ⚡ Verificación rápida
- ⚡ Pasos siguientes

**Tiempo de lectura:** 2 minutos

---

### 3. [`README.md`](README.md) 📖
**¿Cuándo leer?** Para entender qué hace el proyecto.

**Contenido:**
- Descripción de los endpoints (PaygoldLink, DecryptAndRedirect)
- Instrucciones de ejecución local
- Instrucciones de despliegue
- Variables de entorno necesarias

**Tiempo de lectura:** 5 minutos

---

## 📋 Documentación Técnica

### 4. [`SOLUCION_PROBLEMA_RECURRENTE.md`](SOLUCION_PROBLEMA_RECURRENTE.md)
**¿Cuándo leer?** Para entender en profundidad por qué ocurría el problema.

**Contenido:**
- Por qué ocurre el problema recurrente
- Explicación técnica del `sys.path`
- Solución paso a paso
- Pruebas de estrés
- Opciones avanzadas si el problema persiste

**Tiempo de lectura:** 15 minutos

---

### 5. [`CAMBIOS_REALIZADOS.md`](CAMBIOS_REALIZADOS.md)
**¿Cuándo leer?** Para ver qué cambios se hicieron en el proyecto.

**Contenido:**
- Archivos nuevos creados
- Archivos modificados
- Comparación antes vs después
- Configuraciones críticas añadidas

**Tiempo de lectura:** 10 minutos

---

### 6. [`SOLUCION_DEPENDENCIAS_RESUMEN.md`](SOLUCION_DEPENDENCIAS_RESUMEN.md)
**¿Cuándo leer?** Contexto histórico del problema (versión anterior).

**Contenido:**
- Resumen ejecutivo de la primera solución
- Archivos creados inicialmente
- Instrucciones de despliegue (versión 1.0)

**Nota:** Este documento es histórico. La solución definitiva está en `PROBLEMA_RESUELTO.md`.

---

### 7. [`FIX_RAPIDO.md`](FIX_RAPIDO.md)
**¿Cuándo leer?** Si necesitas una solución rápida (similar a EJECUTAR_AHORA.md).

**Contenido:**
- Solución en 1-2 comandos
- Verificación
- Referencias a documentación completa

**Tiempo de lectura:** 3 minutos

---

## 🛠️ Scripts y Herramientas

### 8. [`deploy.ps1`](deploy.ps1) ⭐ **USAR SIEMPRE**
**Script de despliegue automático para Windows.**

**Qué hace:**
- ✅ Limpia archivos locales
- ✅ Configura `WEBSITE_RUN_FROM_PACKAGE=0` y otras settings críticas
- ✅ Reinicia la Function App
- ✅ Despliega con Remote Build
- ✅ Verifica que todo funcione

**Uso:**
```powershell
.\deploy.ps1 -FunctionAppName "suitechredsys"
```

---

### 9. [`deploy.sh`](deploy.sh)
**Script de despliegue automático para Linux/Mac.**

**Uso:**
```bash
./deploy.sh suitechredsys
```

---

### 10. [`verify_deployment.ps1`](verify_deployment.ps1) ⭐
**Script de verificación post-despliegue.**

**Qué hace:**
- ✅ Verifica configuraciones críticas
- ✅ Prueba el endpoint
- ✅ Revisa logs buscando errores
- ✅ Da un reporte completo

**Uso:**
```powershell
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"
```

---

## 📂 Guías Específicas (Carpeta GUIAS/)

### 11. [`GUIAS/GUIA_PUBLICAR_AZURE.md`](GUIAS/GUIA_PUBLICAR_AZURE.md)
Cómo publicar la función en Azure paso a paso.

### 12. [`GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md`](GUIAS/GUIA_SOLUCIONAR_DEPENDENCIAS.md)
Guía completa para solucionar problemas de dependencias (versión detallada).

### 13. [`GUIAS/GUIA_VER_LOGS_AZURE.md`](GUIAS/GUIA_VER_LOGS_AZURE.md)
Cómo ver y analizar logs en Azure.

### 14. [`GUIAS/GUIA_DESARROLLO.md`](GUIAS/GUIA_DESARROLLO.md)
Guía para desarrolladores que trabajan en el proyecto.

### 15. [`GUIAS/GUIA_POSTMAN.md`](GUIAS/GUIA_POSTMAN.md)
Cómo probar las funciones con Postman.

### 16. [`GUIAS/GUIA_INTEGRACION_REDSYS_BC.md`](GUIAS/GUIA_INTEGRACION_REDSYS_BC.md)
Integración entre RedSys y Business Central.

### 17. [`GUIAS/GUIA_CONFIGURACION_SECRETS.md`](GUIAS/GUIA_CONFIGURACION_SECRETS.md)
Cómo configurar secretos y variables de entorno.

### 18. [`GUIAS/GUIA_PRUEBAS_Y_TABLA.md`](GUIAS/GUIA_PRUEBAS_Y_TABLA.md)
Pruebas y uso de Azure Table Storage.

### 19. [`GUIAS/GUIA_OAUTH_BC.md`](GUIAS/GUIA_OAUTH_BC.md)
Configuración de OAuth para Business Central.

### 20. [`GUIAS/GUIA_INSTALACION_CLIENTE.md`](GUIAS/GUIA_INSTALACION_CLIENTE.md)
Instalación desde el lado del cliente.

---

## 🗂️ Archivos de Configuración

### 21. [`.python_version`](.python_version)
Especifica Python 3.12 para Azure.

### 22. [`requirements.txt`](requirements.txt)
Dependencias Python del proyecto:
- `azure-functions`
- `azure-data-tables`
- `pycryptodome`
- `requests`

### 23. [`host.json`](host.json)
Configuración de Azure Functions (logging, timeout, etc.).

### 24. [`.funcignore`](.funcignore)
Archivos que no deben incluirse en el despliegue.

### 25. [`.deployment`](.deployment)
Configuración de despliegue de Azure.

### 26. [`local.settings.json`](local.settings.json)
Configuración local (no se sube a Azure, incluye secretos).

---

## 🎯 Flujo de Trabajo Recomendado

### Para Nuevos Desarrolladores

1. Lee [`README.md`](README.md) - Entender el proyecto
2. Lee [`GUIAS/GUIA_DESARROLLO.md`](GUIAS/GUIA_DESARROLLO.md) - Setup local
3. Lee [`GUIAS/GUIA_POSTMAN.md`](GUIAS/GUIA_POSTMAN.md) - Probar localmente

### Para Desplegar a Azure

1. Lee [`README.md`](README.md) - Sección de despliegue
2. Ejecuta [`deploy.ps1`](deploy.ps1) - Desplegar
3. Ejecuta [`verify_deployment.ps1`](verify_deployment.ps1) - Verificar

### Si Hay Problemas con Dependencias

1. Lee [`PROBLEMA_RESUELTO.md`](PROBLEMA_RESUELTO.md) ⭐ - Solución definitiva
2. Ejecuta [`deploy.ps1`](deploy.ps1) - Re-desplegar con configuración correcta
3. Si persiste, lee [`SOLUCION_PROBLEMA_RECURRENTE.md`](SOLUCION_PROBLEMA_RECURRENTE.md) - Opciones avanzadas

### Para Emergencias

1. Lee [`EJECUTAR_AHORA.md`](EJECUTAR_AHORA.md) ⚡ - Acción inmediata
2. O lee [`FIX_RAPIDO.md`](FIX_RAPIDO.md) - Alternativa rápida

---

## 📊 Mapa de Documentación por Problema

| Problema | Documento a Leer |
|----------|------------------|
| ❌ `ModuleNotFoundError` recurrente | [`PROBLEMA_RESUELTO.md`](PROBLEMA_RESUELTO.md) ⭐ |
| ❌ Función fallando AHORA | [`EJECUTAR_AHORA.md`](EJECUTAR_AHORA.md) |
| ❓ ¿Cómo desplegar? | [`README.md`](README.md) + [`deploy.ps1`](deploy.ps1) |
| ❓ ¿Cómo verificar despliegue? | [`verify_deployment.ps1`](verify_deployment.ps1) |
| ❓ ¿Qué cambios se hicieron? | [`CAMBIOS_REALIZADOS.md`](CAMBIOS_REALIZADOS.md) |
| ❓ ¿Cómo ver logs? | [`GUIAS/GUIA_VER_LOGS_AZURE.md`](GUIAS/GUIA_VER_LOGS_AZURE.md) |
| ❓ ¿Cómo probar con Postman? | [`GUIAS/GUIA_POSTMAN.md`](GUIAS/GUIA_POSTMAN.md) |
| ❓ ¿Cómo funciona el proyecto? | [`README.md`](README.md) |
| ❓ ¿Cómo configurar variables? | [`GUIAS/GUIA_CONFIGURACION_SECRETS.md`](GUIAS/GUIA_CONFIGURACION_SECRETS.md) |

---

## 🏆 Documentos Más Importantes (Top 5)

1. **[`PROBLEMA_RESUELTO.md`](PROBLEMA_RESUELTO.md)** ⭐⭐⭐⭐⭐
   - Solución definitiva al problema recurrente
   - Verificado y probado

2. **[`README.md`](README.md)** ⭐⭐⭐⭐⭐
   - Documentación principal del proyecto
   - Punto de partida para todo

3. **[`deploy.ps1`](deploy.ps1)** ⭐⭐⭐⭐⭐
   - Script de despliegue (USAR SIEMPRE)
   - Configura todo automáticamente

4. **[`EJECUTAR_AHORA.md`](EJECUTAR_AHORA.md)** ⭐⭐⭐⭐
   - Solución de emergencia
   - 2 comandos para resolver el problema

5. **[`verify_deployment.ps1`](verify_deployment.ps1)** ⭐⭐⭐⭐
   - Verificación automática
   - Confirma que todo funciona

---

## 📝 Notas Finales

### Estado del Proyecto
✅ **PROBLEMA RESUELTO** (12/12/2025)

### Configuración Crítica
⭐ **`WEBSITE_RUN_FROM_PACKAGE=0`** - La más importante

### Próximos Pasos
1. Usar siempre `deploy.ps1` para desplegar
2. Monitorear logs ocasionalmente
3. Mantener esta documentación actualizada

---

**Última actualización:** 12 de diciembre de 2025  
**Total de documentos:** 26+  
**Estado:** ✅ Completo y actualizado

