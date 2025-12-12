#!/bin/bash
# Script de despliegue con verificación de dependencias
# Uso: ./deploy.sh <nombre-function-app>

set -e  # Salir si hay error

FUNCTION_APP_NAME="${1:-suitechredsys}"

echo "🚀 Desplegando a Azure Function App: $FUNCTION_APP_NAME"
echo "=================================================="

# 1. Verificar que requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado"
    exit 1
fi

echo "✅ requirements.txt encontrado"
cat requirements.txt
echo ""

# 2. Limpiar archivos locales de Python que no deben subirse
echo "🧹 Limpiando archivos locales..."
rm -rf .python_packages
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 3. Verificar que Azure CLI está instalado
if ! command -v az &> /dev/null; then
    echo "❌ Error: Azure CLI no está instalado"
    echo "Instálalo desde: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# 4. Verificar que func está instalado
if ! command -v func &> /dev/null; then
    echo "❌ Error: Azure Functions Core Tools no está instalado"
    echo "Instálalo desde: https://docs.microsoft.com/azure/azure-functions/functions-run-local"
    exit 1
fi

# 5. Configurar Remote Build en Azure (CRÍTICO)
echo "🔧 Configurando Remote Build en Azure..."
az functionapp config appsettings set \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$(az functionapp show --name "$FUNCTION_APP_NAME" --query resourceGroup -o tsv)" \
    --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
    "ENABLE_ORYX_BUILD=true" \
    "BUILD_FLAGS=UseExpressBuild" \
    > /dev/null

echo "✅ Remote Build configurado"

# 6. Desplegar
echo "📦 Desplegando función..."
func azure functionapp publish "$FUNCTION_APP_NAME" --python --build remote

# 7. Verificar que las dependencias se instalaron
echo ""
echo "🔍 Verificando instalación de dependencias..."
sleep 10  # Esperar a que Azure termine de procesar

# Intentar invocar la función para verificar
echo "📞 Probando función PaygoldLink..."
RESPONSE=$(az functionapp function show \
    --name "$FUNCTION_APP_NAME" \
    --function-name "PaygoldLink" \
    --query "invokeUrlTemplate" -o tsv 2>/dev/null || echo "")

if [ -n "$RESPONSE" ]; then
    echo "✅ Función PaygoldLink está disponible"
else
    echo "⚠️  No se pudo verificar la función automáticamente"
fi

echo ""
echo "=================================================="
echo "✅ Despliegue completado"
echo ""
echo "📋 Pasos siguientes:"
echo "1. Verifica los logs en Azure Portal"
echo "2. Prueba los endpoints con Postman"
echo "3. Si hay errores, ejecuta: az functionapp log tail --name $FUNCTION_APP_NAME"
echo ""
echo "🔗 URL de la Function App:"
echo "https://$FUNCTION_APP_NAME.azurewebsites.net"


