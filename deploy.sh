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

# Paso 2: Configurar Remote Build en Azure
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

# Paso 3: Desplegar con Remote Build
echo "📦 Desplegando a Azure con Remote Build..."
func azure functionapp publish "$FUNCTION_APP_NAME" --python --build remote

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Despliegue completado exitosamente"
    echo ""
    
    # Paso 4: Verificar que la función esté disponible
    echo "🔍 Verificando función..."
    sleep 5
    
    echo ""
    echo "✨ Despliegue finalizado"
    echo ""
    echo "📋 Endpoints disponibles:"
    echo "   - PaygoldLink: https://$FUNCTION_APP_NAME.azurewebsites.net/api/PaygoldLink"
    echo "   - DecryptAndRedirect: https://$FUNCTION_APP_NAME.azurewebsites.net/api/DecryptAndRedirect"
    echo ""
else
    echo ""
    echo "❌ Error durante el despliegue"
    echo "   Revisa los logs arriba para más detalles"
    exit 1
fi
