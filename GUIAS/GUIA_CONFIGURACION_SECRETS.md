# 🔐 Guía de Configuración - Secrets y Environments en GitHub

Esta guía es para el **proveedor** que debe configurar GitHub Actions para desplegar en el tenant del cliente.

---

## 📋 Información Requerida del Cliente

Antes de empezar, necesitas que el cliente te proporcione la siguiente información (según `GUIA_INSTALACION_CLIENTE.md`):

✅ **Subscription ID**  
✅ **Tenant ID**  
✅ **Client ID (Application ID)**  
✅ **Client Secret Value**  
✅ **Function App Name**  
✅ **Resource Group Name** (opcional, pero útil)  
✅ **Storage Account Name** (opcional, pero útil)  
✅ **Region** (opcional, pero útil)  

---

## 🎯 Paso 1: Crear GitHub Environment

1. Ve a tu repositorio en GitHub
2. Haz clic en **Settings** (Configuración)
3. En el menú lateral, selecciona **Environments**
4. Haz clic en **New environment**
5. Ingresa el nombre del environment:
   - Ejemplos:
     - `cliente-prod` (para producción del cliente)
     - `cliente-nombre-empresa` (si tienes varios clientes)
     - `production-cliente` (si quieres diferenciarlo de tu propio `production`)
6. Haz clic en **Configure environment**
7. Puedes dejar las opciones de protección en blanco por ahora, o configurarlas después
8. Haz clic en **Save protection rules**

---

## 🔐 Paso 2: Configurar Secrets en el Environment

Ahora vamos a agregar los secrets al environment recién creado:

1. En la página del Environment que acabas de crear, verás una sección **"Environment secrets"**
2. Haz clic en **"Add secret"**

Agrega los siguientes secrets **uno por uno**:

### Secret 1: AZURE_SUBSCRIPTION_ID
- **Name**: `AZURE_SUBSCRIPTION_ID`
- **Value**: (el Subscription ID que te proporcionó el cliente)
- Haz clic en **Add secret**

### Secret 2: AZURE_TENANT_ID
- **Name**: `AZURE_TENANT_ID`
- **Value**: (el Tenant ID que te proporcionó el cliente)
- Haz clic en **Add secret**

### Secret 3: AZURE_CLIENT_ID
- **Name**: `AZURE_CLIENT_ID`
- **Value**: (el Client ID / Application ID que te proporcionó el cliente)
- Haz clic en **Add secret**

### Secret 4: AZURE_CLIENT_SECRET
- **Name**: `AZURE_CLIENT_SECRET`
- **Value**: (el Client Secret Value que te proporcionó el cliente)
  - ⚠️ **IMPORTANTE**: Este es el valor del secret, NO el ID del secret
- Haz clic en **Add secret**

### Secret 5: AZURE_FUNCTIONAPP_NAME
- **Name**: `AZURE_FUNCTIONAPP_NAME`
- **Value**: (el nombre de la Function App que creó el cliente)
- Haz clic en **Add secret**

---

## ✅ Verificación de Secrets Configurados

Verifica que tienes estos 5 secrets en el Environment:

- ✅ `AZURE_SUBSCRIPTION_ID`
- ✅ `AZURE_TENANT_ID`
- ✅ `AZURE_CLIENT_ID`
- ✅ `AZURE_CLIENT_SECRET`
- ✅ `AZURE_FUNCTIONAPP_NAME`

---

## 🔄 Paso 3: Actualizar el Workflow de GitHub Actions

El workflow ya debería estar configurado para usar environments, pero si necesitas modificarlo o verificarlo:

1. Ve a `.github/workflows/master_suitechredsys.yml`
2. Verifica que el workflow tenga:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: cliente-prod  # ← Nombre del environment que creaste
    steps:
      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          allow-no-subscriptions: false

      - name: 'Deploy to Azure Functions'
        uses: Azure/functions-action@v1
        with:
          app-name: ${{ secrets.AZURE_FUNCTIONAPP_NAME }}
          slot-name: 'Production'
          package: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
```

**NOTA**: Los secrets ahora se leen del environment automáticamente cuando usas `environment: cliente-prod`

---

## 🧪 Paso 4: Probar el Despliegue

1. **Opción A - Despliegue Manual**:
   - Ve a **Actions** en tu repositorio
   - Selecciona el workflow
   - Haz clic en **"Run workflow"**
   - Selecciona el environment que creaste
   - Haz clic en **"Run workflow"**

2. **Opción B - Push a master**:
   - Haz un pequeño cambio y haz push a la rama `master`
   - El workflow se ejecutará automáticamente

3. **Verificar el resultado**:
   - En la pestaña **Actions**, verifica que el workflow se completó exitosamente
   - Si hay errores, revisa los logs

---

## 🔍 Solución de Problemas Comunes

### Error: "Authentication failed"
- ✅ Verifica que el **Client Secret** no haya expirado
- ✅ Verifica que copiaste el **Value** del secret, no el ID
- ✅ Verifica que el Service Principal tiene permisos de **Contributor** en la Subscription

### Error: "Function App not found"
- ✅ Verifica que el nombre de la Function App sea correcto (case-sensitive)
- ✅ Verifica que la Function App existe en Azure Portal

### Error: "Subscription not found"
- ✅ Verifica que el Subscription ID es correcto
- ✅ Verifica que el Service Principal tiene acceso a esa Subscription

### Error: "Access denied"
- ✅ Verifica que el Service Principal tiene el rol **Contributor** en la Subscription
- ✅ Puede tardar unos minutos en propagarse los permisos

---

## 📝 Template para Solicitar Información al Cliente

Cuando solicites la información al cliente, puedes usar este template:

```
Hola [Cliente],

Para configurar el despliegue automático, necesito la siguiente información 
después de que hayas creado los recursos en Azure:

✅ Subscription ID
✅ Tenant ID  
✅ Client ID (Application ID)
✅ Client Secret Value
✅ Function App Name

Por favor, sigue la guía GUIA_INSTALACION_CLIENTE.md y comparte esta información 
de forma segura (preferiblemente por Teams o un canal seguro, no por email sin cifrar).

Gracias.
```

---

## 🔄 Gestión de Múltiples Clientes

Si tienes varios clientes, crea un **Environment por cada cliente**:

- `cliente-empresa-a-prod`
- `cliente-empresa-b-prod`
- `cliente-empresa-c-prod`

Cada environment tendrá sus propios secrets con los valores específicos de ese cliente.

En el workflow, puedes usar:

```yaml
environment: ${{ github.event.inputs.environment || 'production' }}
```

Para poder seleccionar el environment manualmente al ejecutar el workflow.

---

## 🔒 Seguridad

⚠️ **IMPORTANTE**:

- Los secrets en GitHub están cifrados y solo son accesibles dentro del workflow
- **NUNCA** commitees secrets al código
- Los secrets están ligados al environment, así que cada cliente tiene sus propios secrets aislados
- Si un secret se compromete, el cliente debe crear uno nuevo en Azure Portal

---

## 📚 Referencias

- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Azure Service Principal Authentication](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)


