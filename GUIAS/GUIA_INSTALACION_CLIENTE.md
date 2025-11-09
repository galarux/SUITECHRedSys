# 📋 Guía de Instalación - Recursos Azure para SUITECHRedSys

Esta guía está destinada al **cliente** que debe crear los recursos de Azure en su tenant.

---

## 📋 Información Requerida ANTES de Empezar

Antes de crear los recursos, necesitas tener:
- ✅ Acceso al [Azure Portal](https://portal.azure.com)
- ✅ Permisos de **Contributor** o **Owner** en una suscripción de Azure
- ✅ Subscription ID de Azure

---

## 🎯 Recursos que se deben crear

1. **Resource Group** (Grupo de Recursos)
2. **Storage Account** (Cuenta de Almacenamiento)
3. **Function App** (Aplicación de Funciones)
4. **Azure Table Storage** (Tabla de Almacenamiento) - Se crea automáticamente cuando se use

---

## 🚀 Paso 1: Crear Resource Group

1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca **"Resource groups"** en la barra de búsqueda
3. Haz clic en **"+ Create"**
4. Completa:
   - **Subscription**: Selecciona tu suscripción
   - **Resource group**: `rg-suitech-redsys` (o el nombre que prefieras)
   - **Region**: Selecciona la región más cercana (ej: `West Europe`, `East US`, etc.)
5. Haz clic en **"Review + Create"** y luego **"Create"**

📝 **Anota el nombre del Resource Group**: _______________________

---

## 💾 Paso 2: Crear Storage Account

1. En Azure Portal, busca **"Storage accounts"**
2. Haz clic en **"+ Create"**
3. Completa la pestaña **"Basics"**:
   - **Subscription**: La misma suscripción
   - **Resource group**: Selecciona el Resource Group creado en el Paso 1
   - **Storage account name**: Debe ser **único globalmente**
     - Ejemplo: `stsuitechredsys12345` (añade números aleatorios)
     - Solo letras minúsculas y números, sin guiones ni espacios
   - **Region**: La misma región del Resource Group
   - **Performance**: `Standard`
   - **Redundancy**: `Locally redundant storage (LRS)` (suficiente para desarrollo)
4. Haz clic en **"Review"** y luego **"Create"**
5. Espera a que termine el despliegue (1-2 minutos)

📝 **Anota el nombre del Storage Account**: _______________________

---

## ⚡ Paso 3: Crear Function App

1. En Azure Portal, busca **"Function App"**
2. Haz clic en **"+ Create"**
3. Completa la pestaña **"Basics"**:
   - **Subscription**: La misma suscripción
   - **Resource group**: El mismo Resource Group
   - **Function App name**: Debe ser **único globalmente**
     - Ejemplo: `func-suitech-redsys-prod` (añade sufijos únicos)
     - Solo letras minúsculas, números y guiones
   - **Publish**: `Code`
   - **Runtime stack**: `Python`
   - **Version**: `3.12` (o la más reciente disponible)
   - **Region**: La misma región
   - **Operating System**: `Linux` ⚠️ **IMPORTANTE: Selecciona Linux**
   - **Plan type**: `Consumption (Serverless)` ⚠️ **IMPORTANTE**
4. Haz clic en **"Next: Storage"**
5. En la pestaña **"Storage"**:
   - **Storage account**: Selecciona el Storage Account creado en el Paso 2
   - **Application Insights**: Puedes dejar habilitado o deshabilitarlo (opcional)
6. Haz clic en **"Review + Create"** y luego **"Create"**
7. Espera a que termine el despliegue (2-3 minutos)

📝 **Anota el nombre de la Function App**: _______________________

---

## 🔧 Paso 4: Registrar un Service Principal (App Registration)

Para que GitHub Actions pueda desplegar automáticamente, necesitas crear una **App Registration**:

1. En Azure Portal, busca **"Azure Active Directory"** o **"Microsoft Entra ID"**
2. En el menú lateral, selecciona **"App registrations"**
3. Haz clic en **"+ New registration"**
4. Completa:
   - **Name**: `github-actions-suitech-redsys` (o el nombre que prefieras)
   - **Supported account types**: `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI**: Déjalo vacío
5. Haz clic en **"Register"**
6. **IMPORTANTE - Anota estos valores**:
   - **Application (client) ID**: Se muestra en la página principal
     - 📝 **Anota el Client ID**: _______________________
   - **Directory (tenant) ID**: Se muestra en la página principal
     - 📝 **Anota el Tenant ID**: _______________________

7. Ahora necesitas crear un **Secret (Client Secret)**:
   - En el menú lateral, selecciona **"Certificates & secrets"**
   - Haz clic en **"+ New client secret"**
   - **Description**: `GitHub Actions Deployment`
   - **Expires**: `24 months` (o el periodo que prefieras)
   - Haz clic en **"Add"**
   - ⚠️ **IMPORTANTE**: Copia el **Value** del secret **INMEDIATAMENTE** (solo se muestra una vez)
     - 📝 **Anota el Client Secret Value**: _______________________

8. Ahora necesitas asignar permisos a la App Registration:
   - En Azure Portal, ve a tu **Subscription**
   - Selecciona **"Access control (IAM)"** en el menú lateral
   - Haz clic en **"+ Add"** → **"Add role assignment"**
   - **Role**: Selecciona **"Contributor"**
   - **Assign access to**: Selecciona **"User, group, or service principal"**
   - Haz clic en **"+ Select members"**
   - Busca el nombre de tu App Registration (ej: `github-actions-suitech-redsys`)
   - Selecciona y haz clic en **"Select"**
   - Haz clic en **"Review + assign"**

---

## 📊 Paso 5: Obtener el Subscription ID

1. En Azure Portal, busca **"Subscriptions"**
2. Haz clic en tu suscripción
3. Copia el **Subscription ID**
   - 📝 **Anota el Subscription ID**: _______________________

---

## ✅ Checklist Final - Información para el Proveedor

Una vez completados todos los pasos, proporciona esta información al proveedor:

### Información de Azure
- [ ] **Subscription ID**: _______________________
- [ ] **Tenant ID**: _______________________
- [ ] **Resource Group Name**: _______________________
- [ ] **Function App Name**: _______________________
- [ ] **Storage Account Name**: _______________________
- [ ] **Region**: _______________________

### Información de Service Principal (App Registration)
- [ ] **Client ID (Application ID)**: _______________________
- [ ] **Client Secret Value**: _______________________
  - ⚠️ **NOTA**: Si ya expiró o se perdió, hay que crear uno nuevo en "Certificates & secrets"

### Información Adicional
- [ ] **URL de la Function App**: `https://[NOMBRE-FUNCTION-APP].azurewebsites.net`
  - Esta URL se muestra en la página Overview de la Function App

---

## 🔍 Verificación

Antes de enviar la información, verifica que:

1. ✅ La Function App está **Running** (puedes verlo en Azure Portal)
2. ✅ El Service Principal tiene permisos de **Contributor** en la Subscription
3. ✅ Has copiado correctamente todos los IDs (sin espacios extra)
4. ✅ El Client Secret está guardado de forma segura (no compartir por email sin cifrar)

---

## 📞 Soporte

Si tienes problemas durante la instalación, contacta con el proveedor proporcionando:
- Capturas de pantalla del error
- Pasos que ya completaste
- Mensajes de error específicos

---

## 🔒 Seguridad

⚠️ **IMPORTANTE**:
- El **Client Secret** es información sensible. Compártelo de forma segura (ej: por Teams, mediante un administrador de secrets, etc.)
- No compartas los secrets por email sin cifrar
- Una vez configurado el despliegue, puedes revocar o rotar los secrets si es necesario

---

## 📝 Notas Adicionales

- Los nombres de **Storage Account** y **Function App** deben ser únicos globalmente en Azure
- Si un nombre ya está en uso, prueba añadiendo números o sufijos únicos
- El Resource Group puede tener el mismo nombre en diferentes suscripciones (no requiere ser único globalmente)


