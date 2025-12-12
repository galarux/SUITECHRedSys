# Script de verificación post-despliegue
# Uso: .\verify_deployment.ps1 -FunctionAppName "suitechredsys"

param(
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName = "suitechredsys"
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Verificando despliegue de Azure Function App: $FunctionAppName" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Obtener resource group
Write-Host "📋 Obteniendo información de la Function App..." -ForegroundColor Yellow
$resourceGroup = az functionapp show --name $FunctionAppName --query resourceGroup -o tsv

if (-not $resourceGroup) {
    Write-Host "❌ No se pudo encontrar la Function App '$FunctionAppName'" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Resource Group: $resourceGroup" -ForegroundColor Green
Write-Host ""

# 2. Verificar configuración crítica
Write-Host "🔧 Verificando configuración crítica..." -ForegroundColor Yellow
$settings = az functionapp config appsettings list --name $FunctionAppName --resource-group $resourceGroup -o json | ConvertFrom-Json

$criticalSettings = @{
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "ENABLE_ORYX_BUILD" = "true"
    "WEBSITE_RUN_FROM_PACKAGE" = "0"
    "FUNCTIONS_WORKER_RUNTIME" = "python"
}

$configOk = $true

foreach ($settingName in $criticalSettings.Keys) {
    $expectedValue = $criticalSettings[$settingName]
    $setting = $settings | Where-Object { $_.name -eq $settingName }
    
    if ($setting) {
        if ($setting.value -eq $expectedValue) {
            Write-Host "  ✅ $settingName = $($setting.value)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $settingName = $($setting.value) (esperado: $expectedValue)" -ForegroundColor Yellow
            $configOk = $false
        }
    } else {
        Write-Host "  ❌ $settingName no configurado" -ForegroundColor Red
        $configOk = $false
    }
}

Write-Host ""

# 3. Verificar que las funciones existen
Write-Host "📦 Verificando funciones desplegadas..." -ForegroundColor Yellow
$functions = az functionapp function list --name $FunctionAppName --resource-group $resourceGroup -o json | ConvertFrom-Json

$expectedFunctions = @("PaygoldLink", "DecryptAndRedirect")
$functionsOk = $true

foreach ($funcName in $expectedFunctions) {
    $func = $functions | Where-Object { $_.name -eq $funcName }
    if ($func) {
        Write-Host "  ✅ $funcName encontrada" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $funcName NO encontrada" -ForegroundColor Red
        $functionsOk = $false
    }
}

Write-Host ""

# 4. Probar endpoint PaygoldLink
Write-Host "🧪 Probando endpoint PaygoldLink..." -ForegroundColor Yellow
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

$endpointOk = $false

try {
    $response = Invoke-WebRequest -Uri $functionUrl -Method POST -Body $testBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ Endpoint responde correctamente (HTTP 200)" -ForegroundColor Green
        Write-Host "  ✅ Las dependencias están instaladas" -ForegroundColor Green
        $endpointOk = $true
    }
} catch {
    $errorMessage = $_.Exception.Message
    
    if ($errorMessage -like "*ModuleNotFoundError*" -or $errorMessage -like "*No module named*") {
        Write-Host "  ❌ ERROR CRÍTICO: ModuleNotFoundError detectado" -ForegroundColor Red
        Write-Host "  ❌ Las dependencias NO están instaladas correctamente" -ForegroundColor Red
        Write-Host ""
        Write-Host "  🔧 Solución: Ejecuta .\deploy.ps1 -FunctionAppName $FunctionAppName" -ForegroundColor Yellow
    } elseif ($errorMessage -like "*500*") {
        Write-Host "  ⚠️  Endpoint responde con error 500 (puede ser normal en test)" -ForegroundColor Yellow
        Write-Host "  ℹ️  Verifica los logs para confirmar que no es error de módulos" -ForegroundColor Cyan
    } elseif ($errorMessage -like "*404*") {
        Write-Host "  ❌ Endpoint no encontrado (404)" -ForegroundColor Red
        Write-Host "  ℹ️  La función puede no estar desplegada correctamente" -ForegroundColor Cyan
    } else {
        Write-Host "  ⚠️  Error al probar endpoint: $errorMessage" -ForegroundColor Yellow
    }
}

Write-Host ""

# 5. Obtener logs recientes
Write-Host "📊 Últimos logs (últimos 50 mensajes)..." -ForegroundColor Yellow
Write-Host "  (Buscando errores de módulos...)" -ForegroundColor Gray

try {
    $logs = az functionapp log tail --name $FunctionAppName --resource-group $resourceGroup --timeout 5 2>&1
    
    $hasModuleError = $false
    foreach ($line in $logs) {
        if ($line -like "*ModuleNotFoundError*" -or $line -like "*No module named*") {
            Write-Host "  ❌ Error de módulo detectado en logs" -ForegroundColor Red
            $hasModuleError = $true
            break
        }
    }
    
    if (-not $hasModuleError) {
        Write-Host "  ✅ No se detectaron errores de módulos en logs recientes" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️  No se pudieron obtener logs automáticamente" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan

# 6. Resumen final
$allOk = $configOk -and $functionsOk -and $endpointOk

if ($allOk) {
    Write-Host "✅ VERIFICACIÓN EXITOSA - Todo funcionando correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 La Function App está lista para usar" -ForegroundColor Green
} else {
    Write-Host "⚠️  VERIFICACIÓN COMPLETADA CON PROBLEMAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Acciones recomendadas:" -ForegroundColor Yellow
    
    if (-not $configOk) {
        Write-Host "  1. Ejecuta: .\deploy.ps1 -FunctionAppName $FunctionAppName" -ForegroundColor White
    }
    
    if (-not $functionsOk) {
        Write-Host "  2. Verifica que el código esté completo en el repositorio" -ForegroundColor White
    }
    
    if (-not $endpointOk) {
        Write-Host "  3. Revisa los logs: az functionapp log tail --name $FunctionAppName --resource-group $resourceGroup" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
Write-Host "  Ver logs en tiempo real:" -ForegroundColor White
Write-Host "    az functionapp log tail --name $FunctionAppName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host ""
Write-Host "  Reiniciar Function App:" -ForegroundColor White
Write-Host "    az functionapp restart --name $FunctionAppName --resource-group $resourceGroup" -ForegroundColor Gray
Write-Host ""
Write-Host "  Re-desplegar:" -ForegroundColor White
Write-Host "    .\deploy.ps1 -FunctionAppName $FunctionAppName" -ForegroundColor Gray
Write-Host ""

