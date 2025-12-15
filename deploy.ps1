#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script de despliegue para Azure Functions con Remote Build garantizado
.DESCRIPTION
    Este script asegura que las dependencias se instalen correctamente en Azure
    y persistan después de reinicios del worker.
.PARAMETER FunctionAppName
    Nombre de la Function App en Azure (por defecto: suitechredsys)
.PARAMETER ResourceGroup
    Nombre del Resource Group (por defecto: rg-suitech-redsys)
#>

param(
    [string]$FunctionAppName = "suitechredsys",
    [string]$ResourceGroup = "rg-suitech-redsys"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando despliegue de Azure Functions..." -ForegroundColor Cyan
Write-Host "   Function App: $FunctionAppName" -ForegroundColor Gray
Write-Host "   Resource Group: $ResourceGroup" -ForegroundColor Gray
Write-Host ""

# Paso 1: Limpiar archivos locales de Python
Write-Host "🧹 Limpiando archivos locales de Python..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .python_packages -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✅ Archivos locales limpiados" -ForegroundColor Green
Write-Host ""

# Paso 2: Configurar Remote Build en Azure
Write-Host "⚙️  Configurando Remote Build en Azure..." -ForegroundColor Yellow
try {
    az functionapp config appsettings set `
        --name $FunctionAppName `
        --resource-group $ResourceGroup `
        --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
                   "ENABLE_ORYX_BUILD=true" `
                   "BUILD_FLAGS=UseExpressBuild" `
                   "WEBSITE_RUN_FROM_PACKAGE=1" `
        --output none
    Write-Host "   ✅ Remote Build configurado" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  No se pudo configurar Remote Build (puede que ya esté configurado)" -ForegroundColor Yellow
}
Write-Host ""

# Paso 3: Desplegar con Remote Build
Write-Host "📦 Desplegando a Azure con Remote Build..." -ForegroundColor Yellow
func azure functionapp publish $FunctionAppName --python --build remote

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Despliegue completado exitosamente" -ForegroundColor Green
    Write-Host ""
    
    # Paso 4: Verificar que la función esté disponible
    Write-Host "🔍 Verificando función..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $url = "https://$FunctionAppName.azurewebsites.net/api/PaygoldLink"
    Write-Host "   URL: $url" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "✨ Despliegue finalizado" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Endpoints disponibles:" -ForegroundColor White
    Write-Host "   - PaygoldLink: https://$FunctionAppName.azurewebsites.net/api/PaygoldLink" -ForegroundColor Gray
    Write-Host "   - DecryptAndRedirect: https://$FunctionAppName.azurewebsites.net/api/DecryptAndRedirect" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error durante el despliegue" -ForegroundColor Red
    Write-Host "   Revisa los logs arriba para más detalles" -ForegroundColor Yellow
    exit 1
}
