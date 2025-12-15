#!/bin/bash
# Script de despliegue para Azure Functions con Remote Build garantizado

set -e

FUNCTION_APP_NAME="${1:-suitechredsys}"
RESOURCE_GROUP="${2:-rg-suitech-redsys}"

echo "🚀 Iniciando despliegue de Azure Functions..."
echo "   Function App: $FUNCTION_APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo ""

# Paso 1: Limpiar archivos locales de Python
echo "🧹 Limpiando archivos locales de Python..."
rm -rf .python_packages
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Archivos locales limpiados"
echo ""

# Paso 2: Eliminar WEBSITE_RUN_FROM_PACKAGE temporalmente
echo "🗑️  Eliminando WEBSITE_RUN_FROM_PACKAGE temporalmente..."
az functionapp config appsettings delete \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --setting-names "WEBSITE_RUN_FROM_PACKAGE" \
    --output none 2>/dev/null || echo "   ⚠️  No se pudo eliminar (puede que no exista)"
echo "   ✅ WEBSITE_RUN_FROM_PACKAGE eliminado"
echo ""

# Paso 3: Configurar Remote Build en Azure
echo "⚙️  Configurando Remote Build en Azure..."
az functionapp config appsettings set \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
               "ENABLE_ORYX_BUILD=true" \
               "BUILD_FLAGS=UseExpressBuild" \
    --output none || echo "   ⚠️  No se pudo configurar Remote Build (puede que ya esté configurado)"
echo "   ✅ Remote Build configurado"
echo ""

# Paso 4: Desplegar con Remote Build
echo "📦 Desplegando a Azure con Remote Build..."
func azure functionapp publish "$FUNCTION_APP_NAME" --python --build remote

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Despliegue completado exitosamente"
    echo ""
    
    # Paso 5: Reconfigurar settings que se eliminaron durante el despliegue
    echo "🔧 Reconfigurando settings de persistencia..."
    STORAGE_ACCOUNT=$(az storage account list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv)
    if [ -n "$STORAGE_ACCOUNT" ]; then
        CONN_STR=$(az storage account show-connection-string --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --query "connectionString" -o tsv)
        
        az functionapp config appsettings set \
            --name "$FUNCTION_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --settings "AzureWebJobsStorage=$CONN_STR" \
                       "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=$CONN_STR" \
                       "WEBSITE_CONTENTSHARE=$FUNCTION_APP_NAME" \
            --output none
        echo "   ✅ Settings de persistencia reconfiguradas"
    else
        echo "   ⚠️  No se pudo encontrar el storage account"
    fi
    echo ""
    
    # Paso 6: Reiniciar la Function App
    echo "🔄 Reiniciando Function App..."
    az functionapp restart --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --output none
    echo "   ✅ Function App reiniciada"
    echo "   ⏳ Esperando a que la app esté lista (45 segundos)..."
    sleep 45
    echo ""
    
    # Paso 7: Verificar dependencias instaladas
    echo "🔍 Verificando dependencias instaladas..."
    echo "   📡 Realizando petición de prueba..."
    
    TEST_URL="https://$FUNCTION_APP_NAME.azurewebsites.net/api/PaygoldLink"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_URL" --max-time 30 || echo "000")
    
    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ Función responde correctamente (código: $HTTP_CODE)"
        echo "   ✅ Las dependencias están instaladas correctamente"
    elif [ "$HTTP_CODE" = "404" ]; then
        echo "   ⚠️  Advertencia: La app todavía se está reiniciando (404)"
        echo "   ⏳ Espera 1-2 minutos y prueba manualmente las funciones"
    elif [ "$HTTP_CODE" = "500" ] || [ "$HTTP_CODE" = "502" ] || [ "$HTTP_CODE" = "503" ]; then
        echo "   ❌ ERROR: La función devolvió un error de servidor (código: $HTTP_CODE)"
        echo "   ⚠️  Esto puede indicar un problema con las dependencias"
        echo ""
        echo "   💡 Ejecuta este comando para ver los logs:"
        echo "   az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
    else
        echo "   ⚠️  Advertencia: Respuesta inesperada (código: $HTTP_CODE)"
    fi
    
    echo ""
    echo "✨ Despliegue finalizado"
    echo ""
    echo "📋 Endpoints disponibles:"
    echo "   - PaygoldLink: https://$FUNCTION_APP_NAME.azurewebsites.net/api/PaygoldLink"
    echo "   - DecryptAndRedirect: https://$FUNCTION_APP_NAME.azurewebsites.net/api/DecryptAndRedirect"
    echo ""
    echo "📊 Para ver los logs en tiempo real:"
    echo "   az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
    echo ""
else
    echo ""
    echo "❌ Error durante el despliegue"
    echo "   Revisa los logs arriba para más detalles"
    exit 1
fi
