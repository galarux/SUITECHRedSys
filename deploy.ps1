# Script de despliegue con verificación de dependencias (PowerShell)
# Uso: .\deploy.ps1 -FunctionAppName "suitechredsys"

param(
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName = "suitechredsys"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Desplegando a Azure Function App: $FunctionAppName" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Verificar que requirements.txt existe
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: requirements.txt no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "✅ requirements.txt encontrado" -ForegroundColor Green
Get-Content requirements.txt
Write-Host ""

# 2. Limpiar archivos locales de Python que no deben subirse
Write-Host "🧹 Limpiando archivos locales..." -ForegroundColor Yellow
if (Test-Path ".python_packages") {
    Remove-Item -Recurse -Force ".python_packages"
}
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -File -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# 3. Verificar que Azure CLI está instalado
try {
    az --version | Out-Null
} catch {
    Write-Host "❌ Error: Azure CLI no está instalado" -ForegroundColor Red
    Write-Host "Instálalo desde: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# 4. Verificar que func está instalado
try {
    func --version | Out-Null
} catch {
    Write-Host "❌ Error: Azure Functions Core Tools no está instalado" -ForegroundColor Red
    Write-Host "Instálalo desde: https://docs.microsoft.com/azure/azure-functions/functions-run-local" -ForegroundColor Yellow
    exit 1
}

# 5. Configurar Remote Build en Azure (CRÍTICO)
Write-Host "🔧 Configurando Remote Build en Azure..." -ForegroundColor Yellow

$resourceGroup = az functionapp show --name $FunctionAppName --query resourceGroup -o tsv

az functionapp config appsettings set `
    --name $FunctionAppName `
    --resource-group $resourceGroup `
    --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" "ENABLE_ORYX_BUILD=true" "BUILD_FLAGS=UseExpressBuild" `
    | Out-Null

Write-Host "✅ Remote Build configurado" -ForegroundColor Green

# 6. Desplegar
Write-Host "📦 Desplegando función..." -ForegroundColor Yellow
func azure functionapp publish $FunctionAppName --python --build remote

# 7. Verificar que las dependencias se instalaron
Write-Host ""
Write-Host "🔍 Verificando instalación de dependencias..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Intentar invocar la función para verificar
Write-Host "📞 Probando función PaygoldLink..." -ForegroundColor Yellow
try {
    $response = az functionapp function show `
        --name $FunctionAppName `
        --function-name "PaygoldLink" `
        --query "invokeUrlTemplate" -o tsv 2>$null
    
    if ($response) {
        Write-Host "✅ Función PaygoldLink está disponible" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  No se pudo verificar la función automáticamente" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✅ Despliegue completado" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Pasos siguientes:" -ForegroundColor Cyan
Write-Host "1. Verifica los logs en Azure Portal"
Write-Host "2. Prueba los endpoints con Postman"
Write-Host "3. Si hay errores, ejecuta: az functionapp log tail --name $FunctionAppName"
Write-Host ""
Write-Host "🔗 URL de la Function App:" -ForegroundColor Cyan
Write-Host "https://$FunctionAppName.azurewebsites.net"

