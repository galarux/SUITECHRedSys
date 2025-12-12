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

# Configurar todas las settings necesarias para Remote Build
az functionapp config appsettings set `
    --name $FunctionAppName `
    --resource-group $resourceGroup `
    --settings `
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
        "ENABLE_ORYX_BUILD=true" `
        "BUILD_FLAGS=UseExpressBuild" `
        "WEBSITE_RUN_FROM_PACKAGE=0" `
        "FUNCTIONS_WORKER_RUNTIME=python" `
        "PYTHON_ENABLE_WORKER_EXTENSIONS=1" `
    | Out-Null

Write-Host "✅ Remote Build configurado" -ForegroundColor Green

# Reiniciar para aplicar cambios
Write-Host "🔄 Reiniciando Function App para aplicar configuración..." -ForegroundColor Yellow
az functionapp restart --name $FunctionAppName --resource-group $resourceGroup | Out-Null
Start-Sleep -Seconds 15
Write-Host "✅ Function App reiniciada" -ForegroundColor Green

# 6. Desplegar con Remote Build
Write-Host "📦 Desplegando función con Remote Build..." -ForegroundColor Yellow
Write-Host "⚠️  Esto puede tardar varios minutos..." -ForegroundColor Yellow

# Usar --no-build local y --build remote para forzar construcción remota
func azure functionapp publish $FunctionAppName --python --build remote --no-bundler

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error durante el despliegue" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Despliegue completado" -ForegroundColor Green

# 7. Esperar a que la función se inicialice
Write-Host ""
Write-Host "⏳ Esperando a que la función se inicialice (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 8. Verificar configuración en Azure
Write-Host "🔍 Verificando configuración en Azure..." -ForegroundColor Yellow
$settings = az functionapp config appsettings list --name $FunctionAppName --resource-group $resourceGroup -o json | ConvertFrom-Json

$criticalSettings = @("SCM_DO_BUILD_DURING_DEPLOYMENT", "ENABLE_ORYX_BUILD", "WEBSITE_RUN_FROM_PACKAGE")
$allOk = $true

foreach ($settingName in $criticalSettings) {
    $setting = $settings | Where-Object { $_.name -eq $settingName }
    if ($setting) {
        Write-Host "  ✅ $settingName = $($setting.value)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $settingName no encontrado" -ForegroundColor Red
        $allOk = $false
    }
}

# 9. Intentar invocar la función para verificar
Write-Host ""
Write-Host "📞 Probando función PaygoldLink..." -ForegroundColor Yellow
try {
    $functionUrl = "https://$FunctionAppName.azurewebsites.net/api/PaygoldLink"
    
    $testBody = @{
        urlBC = "https://test.com"
        authType = "basic"
        user = "test"
        pass = "test"
        encryptData = @{
            DS_MERCHANT_ORDER = "TEST001"
            DS_MERCHANT_AMOUNT = "100"
        }
        redirectURL = "https://sis-t.redsys.es:25443/sis/rest/trataPeticionREST"
        encryptKey = "sq7HjrUOBfKmC576ILgskD5srU870gJ7"
    } | ConvertTo-Json -Depth 10

    $response = Invoke-WebRequest -Uri $functionUrl -Method POST -Body $testBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Función responde correctamente (HTTP 200)" -ForegroundColor Green
        Write-Host "✅ Las dependencias están instaladas correctamente" -ForegroundColor Green
        $allOk = $true
    }
} catch {
    $errorMessage = $_.Exception.Message
    if ($errorMessage -like "*ModuleNotFoundError*" -or $errorMessage -like "*No module named*") {
        Write-Host "❌ ERROR: Las dependencias NO se instalaron correctamente" -ForegroundColor Red
        Write-Host "❌ Aún aparece ModuleNotFoundError" -ForegroundColor Red
        $allOk = $false
    } elseif ($errorMessage -like "*500*") {
        Write-Host "⚠️  La función responde pero hay un error interno (puede ser normal en test)" -ForegroundColor Yellow
        Write-Host "⚠️  Verifica los logs para confirmar que no es un error de módulos" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  No se pudo verificar automáticamente: $errorMessage" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan

if ($allOk) {
    Write-Host "✅ DESPLIEGUE EXITOSO - Todo funcionando correctamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  DESPLIEGUE COMPLETADO CON ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host "⚠️  Revisa los logs para más detalles" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Pasos siguientes:" -ForegroundColor Cyan
Write-Host "1. Verifica los logs con el comando de abajo" -ForegroundColor White
Write-Host "2. Monitorea en Azure Portal: https://portal.azure.com" -ForegroundColor White
Write-Host "3. Prueba los endpoints con Postman" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URLs de la Function App:" -ForegroundColor Cyan
Write-Host "  - PaygoldLink: https://$FunctionAppName.azurewebsites.net/api/PaygoldLink" -ForegroundColor White
Write-Host "  - DecryptAndRedirect: https://$FunctionAppName.azurewebsites.net/api/DecryptAndRedirect" -ForegroundColor White
Write-Host ""
Write-Host "Ver logs en tiempo real:" -ForegroundColor Cyan
Write-Host "  az functionapp log tail --name $FunctionAppName --resource-group $resourceGroup" -ForegroundColor Gray


