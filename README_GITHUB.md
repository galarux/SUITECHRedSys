# 🚀 SUITECH RedSys Functions

[![Azure Functions](https://img.shields.io/badge/Azure-Functions-blue?logo=microsoft-azure)](https://azure.microsoft.com/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production-success)](https://github.com/galarux/SUITECHRedSys)
[![Problem](https://img.shields.io/badge/ModuleNotFoundError-RESUELTO-success)](PROBLEMA_RESUELTO.md)

Azure Functions en Python que conectan **Business Central** con **RedSys** para procesamiento de pagos.

---

## 🚨 IMPORTANTE - Problema Resuelto

> **✅ PROBLEMA RESUELTO (12/12/2025)**
> 
> El problema recurrente de `ModuleNotFoundError: No module named 'requests'` ha sido **resuelto definitivamente**.
> 
> **Solución:** Configuración `WEBSITE_RUN_FROM_PACKAGE=0` + Remote Build correctamente configurado.
> 
> **Verificado:** ✅ Función funciona después de reiniciar (prueba crítica superada).

📖 **[Ver documentación completa de la solución →](PROBLEMA_RESUELTO.md)**

---

## 📚 Documentación Rápida

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| **[PROBLEMA_RESUELTO.md](PROBLEMA_RESUELTO.md)** ⭐ | Análisis completo y solución definitiva | Si tienes `ModuleNotFoundError` |
| **[EJECUTAR_AHORA.md](EJECUTAR_AHORA.md)** ⚡ | Guía de acción inmediata | Emergencia - función fallando |
| **[CHEAT_SHEET.md](CHEAT_SHEET.md)** 🚀 | Referencia rápida de comandos | Consulta diaria |
| **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** 📊 | Resumen en una página | Lectura rápida |
| **[DOCUMENTACION_INDICE.md](DOCUMENTACION_INDICE.md)** 📚 | Índice completo (26+ docs) | Explorar todo |

---

## 🎯 Inicio Rápido

### Desplegar a Azure

```powershell
# Windows - Despliegue automático
.\deploy.ps1 -FunctionAppName "suitechredsys"

# Verificar que todo esté correcto
.\verify_deployment.ps1 -FunctionAppName "suitechredsys"
```

```bash
# Linux/Mac
./deploy.sh suitechredsys
```

### Ejecutar Localmente

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar local.settings.json con tus claves

# 3. Iniciar
func start
```

**Endpoints locales:**
- `http://localhost:7071/api/paygoldlink`
- `http://localhost:7071/api/decryptandredirect`

---

## 🔧 Endpoints

### PaygoldLink
**POST** `/api/paygoldlink`

Genera un enlace de pago Paygold siguiendo la documentación oficial de RedSys.

**Request:**
```json
{
  "urlBC": "https://api.businesscentral.dynamics.com/...",
  "authType": "oAuth",
  "user": "client_id",
  "pass": "client_secret",
  "encryptData": {
    "DS_MERCHANT_ORDER": "ORDER123",
    "DS_MERCHANT_AMOUNT": "100",
    "DS_MERCHANT_CURRENCY": "978",
    "DS_MERCHANT_MERCHANTCODE": "263100000",
    "DS_MERCHANT_TERMINAL": "49",
    "DS_MERCHANT_TRANSACTIONTYPE": "0"
  },
  "redirectURL": "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST",
  "encryptKey": "your_key_here"
}
```

### DecryptAndRedirect
**POST** `/api/decryptandredirect`

Recibe la notificación de RedSys, valida la firma y notifica a Business Central.

**Request:**
```json
{
  "Ds_SignatureVersion": "HMAC_SHA256_V1",
  "Ds_MerchantParameters": "base64_encoded_params",
  "Ds_Signature": "signature"
}
```

---

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# Azure Storage
AzureWebJobsStorage=DefaultEndpointsProtocol=https;...

# RedSys
REDSYS_SHA256_KEY=your_key
REDSYS_MERCHANT_CODE=263100000
REDSYS_TERMINAL=49
REDSYS_REST_URL=https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST

# Configuraciones Críticas (automáticas con deploy.ps1)
WEBSITE_RUN_FROM_PACKAGE=0                    # ⭐ CRÍTICO
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
FUNCTIONS_WORKER_RUNTIME=python
PYTHON_ENABLE_WORKER_EXTENSIONS=1
```

---

## 🛠️ Tecnologías

- **Azure Functions** - Serverless compute
- **Python 3.12** - Runtime
- **Azure Table Storage** - Almacenamiento de logs
- **RedSys** - Pasarela de pagos
- **Business Central** - ERP
- **Oryx** - Build system

### Dependencias

```txt
azure-functions==1.24.0
azure-data-tables==12.7.0
pycryptodome==3.23.0
requests==2.32.5
```

---

## 📊 Arquitectura

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Cliente   │────────▶│  PaygoldLink     │────────▶│   RedSys    │
│  (Browser)  │         │  Azure Function  │         │  (Pasarela) │
└─────────────┘         └──────────────────┘         └─────────────┘
                                │                            │
                                │                            │
                                ▼                            ▼
                        ┌──────────────────┐         ┌─────────────┐
                        │ Azure Table      │         │   Cliente   │
                        │ Storage (Logs)   │         │  (Callback) │
                        └──────────────────┘         └─────────────┘
                                                             │
                                                             ▼
                                                      ┌─────────────┐
                                                      │DecryptAnd   │
                                                      │Redirect     │
                                                      └─────────────┘
                                                             │
                                                             ▼
                                                      ┌─────────────┐
                                                      │  Business   │
                                                      │  Central    │
                                                      └─────────────┘
```

---

## 🧪 Testing

### Con Postman

```
POST https://suitechredsys.azurewebsites.net/api/paygoldlink?code={{function_key}}
Content-Type: application/json

{...body...}
```

Ver guía completa: [GUIAS/GUIA_POSTMAN.md](GUIAS/GUIA_POSTMAN.md)

### Con curl

```bash
curl -X POST https://suitechredsys.azurewebsites.net/api/paygoldlink \
  -H "Content-Type: application/json" \
  -d '{"urlBC":"...","authType":"basic",...}'
```

---

## 📈 Estado del Proyecto

| Aspecto | Estado |
|---------|--------|
| **Producción** | ✅ Funcionando |
| **Problema ModuleNotFoundError** | ✅ **RESUELTO** |
| **Pruebas** | ✅ Verificado después de reinicio |
| **Documentación** | ✅ Completa (15+ docs) |
| **Scripts Automatizados** | ✅ deploy.ps1 + verify_deployment.ps1 |
| **Configuración** | ✅ WEBSITE_RUN_FROM_PACKAGE=0 |

---

## 🤝 Contribuir

### Workflow de Desarrollo

1. **Clone el repositorio**
   ```bash
   git clone https://github.com/galarux/SUITECHRedSys.git
   cd SUITECHRedSys
   ```

2. **Configura el entorno local**
   ```bash
   pip install -r requirements.txt
   # Edita local.settings.json con tus claves
   ```

3. **Desarrolla y prueba localmente**
   ```bash
   func start
   ```

4. **Despliega a Azure**
   ```powershell
   .\deploy.ps1 -FunctionAppName "suitechredsys"
   ```

### Estructura del Proyecto

```
SUITECH RedSys/
├── PaygoldLink/              # Función para generar enlaces Paygold
├── DecryptAndRedirect/       # Función para procesar notificaciones
├── utils/                    # Utilidades (crypto, storage)
├── GUIAS/                    # 10+ guías detalladas
├── deploy.ps1               # Script de despliegue
├── verify_deployment.ps1    # Script de verificación
└── [15+ documentos]         # Documentación completa
```

---

## 📞 Soporte

### Documentación

- **Problema con dependencias:** [PROBLEMA_RESUELTO.md](PROBLEMA_RESUELTO.md)
- **Guía de despliegue:** [GUIAS/GUIA_PUBLICAR_AZURE.md](GUIAS/GUIA_PUBLICAR_AZURE.md)
- **Ver logs:** [GUIAS/GUIA_VER_LOGS_AZURE.md](GUIAS/GUIA_VER_LOGS_AZURE.md)
- **Comandos rápidos:** [CHEAT_SHEET.md](CHEAT_SHEET.md)
- **Índice completo:** [DOCUMENTACION_INDICE.md](DOCUMENTACION_INDICE.md)

### Comandos Útiles

```bash
# Ver logs en tiempo real
az functionapp log tail --name suitechredsys --resource-group rg-suitech-redsys

# Reiniciar función
az functionapp restart --name suitechredsys --resource-group rg-suitech-redsys

# Ver configuración
az functionapp config appsettings list --name suitechredsys --resource-group rg-suitech-redsys -o table
```

---

## 📝 Changelog

### v3.0.0 - 12/12/2025 ✅ PROBLEMA RESUELTO

**Cambios Críticos:**
- ✅ Añadida configuración `WEBSITE_RUN_FROM_PACKAGE=0` (LA MÁS IMPORTANTE)
- ✅ Configuraciones adicionales de Remote Build
- ✅ Script `deploy.ps1` mejorado con configuración automática
- ✅ Nuevo script `verify_deployment.ps1` para verificación
- ✅ Archivo `.python_version` para especificar Python 3.12

**Documentación:**
- ✅ 10 documentos nuevos creados
- ✅ 3 documentos actualizados
- ✅ Índice completo de documentación
- ✅ Cheat sheet de referencia rápida

**Pruebas:**
- ✅ Función funciona inmediatamente después del despliegue
- ✅ **Función funciona después de reiniciar** (prueba crítica)
- ✅ Dependencias persisten correctamente

**Estado:** ✅ RESUELTO Y VERIFICADO  
**Confianza:** 95%+

### v2.0.0 - Anterior
- ❌ Problema persistía después de 10-15 minutos
- Configuración básica de Remote Build

### v1.0.0 - Inicial
- ❌ Problema recurrente de dependencias
- Funcionalidad básica

---

## 📄 Licencia

Este proyecto es privado y propiedad de SUITECH.

---

## 🏆 Logros

- ✅ **Problema recurrente resuelto definitivamente**
- ✅ **Documentación completa y organizada**
- ✅ **Scripts automatizados funcionando**
- ✅ **Pruebas exitosas (incluyendo reinicio)**
- ✅ **Configuración óptima implementada**

---

**Repositorio:** https://github.com/galarux/SUITECHRedSys  
**Estado:** ✅ Producción - Problema Resuelto  
**Última actualización:** 12 de diciembre de 2025

