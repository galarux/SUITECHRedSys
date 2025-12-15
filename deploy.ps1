param(
    [string]$FunctionAppName = "suitechredsys",
    [string]$ResourceGroup = "rg-suitech-redsys"
)

$ErrorActionPreference = "Stop"

Write-Host "Iniciando despliegue de Azure Functions..." -ForegroundColor Cyan
Write-Host "   Function App: $FunctionAppName" -ForegroundColor Gray
Write-Host "   Resource Group: $ResourceGroup" -ForegroundColor Gray
Write-Host ""

# Paso 1: Limpiar archivos locales de Python
Write-Host "Limpiando archivos locales de Python..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .python_packages -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   Archivos locales limpiados" -ForegroundColor Green
Write-Host ""

# Paso 2: Eliminar WEBSITE_RUN_FROM_PACKAGE temporalmente
Write-Host "Eliminando WEBSITE_RUN_FROM_PACKAGE temporalmente..." -ForegroundColor Yellow
try {
    az functionapp config appsettings delete `
        --name $FunctionAppName `
        --resource-group $ResourceGroup `
        --setting-names "WEBSITE_RUN_FROM_PACKAGE" `
        --output none
    Write-Host "   WEBSITE_RUN_FROM_PACKAGE eliminado" -ForegroundColor Green
} catch {
    Write-Host "   No se pudo eliminar (puede que no exista)" -ForegroundColor Yellow
}
Write-Host ""

# Paso 3: Configurar Remote Build en Azure
Write-Host "Configurando Remote Build en Azure..." -ForegroundColor Yellow
try {
    az functionapp config appsettings set `
        --name $FunctionAppName `
        --resource-group $ResourceGroup `
        --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
                   "ENABLE_ORYX_BUILD=true" `
                   "BUILD_FLAGS=UseExpressBuild" `
        --output none
    Write-Host "   Remote Build configurado" -ForegroundColor Green
} catch {
    Write-Host "   No se pudo configurar Remote Build (puede que ya este configurado)" -ForegroundColor Yellow
}
Write-Host ""

# Paso 4: Desplegar con Remote Build
Write-Host "Desplegando a Azure con Remote Build..." -ForegroundColor Yellow
func azure functionapp publish $FunctionAppName --python --build remote

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Despliegue completado exitosamente" -ForegroundColor Green
    Write-Host ""
    
    # Paso 5: Reconfigurar settings que se eliminaron durante el despliegue
    Write-Host "Reconfigurando settings de persistencia..." -ForegroundColor Yellow
    try {
        # Obtener connection string del storage
        $storageAccount = az storage account list --resource-group $ResourceGroup --query "[0].name" -o tsv
        if ($storageAccount) {
            $connStr = az storage account show-connection-string --name $storageAccount --resource-group $ResourceGroup --query "connectionString" -o tsv
            
            az functionapp config appsettings set `
                --name $FunctionAppName `
                --resource-group $ResourceGroup `
                --settings "AzureWebJobsStorage=$connStr" `
                           "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=$connStr" `
                           "WEBSITE_CONTENTSHARE=$FunctionAppName" `
                --output none
            Write-Host "   Settings de persistencia reconfiguradas" -ForegroundColor Green
        }
    } catch {
        Write-Host "   No se pudieron reconfigurar las settings automaticamente" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Paso 6: Reiniciar la Function App
    Write-Host "Reiniciando Function App..." -ForegroundColor Yellow
    az functionapp restart --name $FunctionAppName --resource-group $ResourceGroup --output none
    Write-Host "   Function App reiniciada" -ForegroundColor Green
    Write-Host "   Esperando a que la app este lista (45 segundos)..." -ForegroundColor Gray
    Start-Sleep -Seconds 45
    Write-Host ""
    
    # Paso 7: Verificar dependencias instaladas
    Write-Host "Verificando dependencias instaladas..." -ForegroundColor Yellow
    
    # Obtener los logs recientes para verificar que no hay errores de ModuleNotFoundError
    Write-Host "   Consultando logs de la aplicacion..." -ForegroundColor Gray
    
    try {
        # Hacer una peticion de prueba a PaygoldLink para forzar la carga de modulos
        $testUrl = "https://$FunctionAppName.azurewebsites.net/api/PaygoldLink"
        Write-Host "   Realizando peticion de prueba a: $testUrl" -ForegroundColor Gray
        
        $response = Invoke-WebRequest -Uri $testUrl -Method GET -ErrorAction SilentlyContinue -TimeoutSec 30
        $statusCode = $response.StatusCode
        
        if ($statusCode -eq 401 -or $statusCode -eq 400) {
            # 401/400 es esperado (falta autenticacion/body), pero significa que la funcion cargo correctamente
            Write-Host "   Funcion responde correctamente (codigo: $statusCode)" -ForegroundColor Green
            Write-Host "   Las dependencias estan instaladas correctamente" -ForegroundColor Green
        } elseif ($statusCode -eq 200) {
            Write-Host "   Funcion responde correctamente (codigo: $statusCode)" -ForegroundColor Green
            Write-Host "   Las dependencias estan instaladas correctamente" -ForegroundColor Green
        } else {
            Write-Host "   Respuesta inesperada (codigo: $statusCode)" -ForegroundColor Yellow
        }
    } catch {
        $errorMessage = $_.Exception.Message
        
        if ($errorMessage -like "*401*" -or $errorMessage -like "*400*") {
            # 401/400 es esperado, significa que la funcion cargo
            Write-Host "   Funcion responde correctamente (requiere autenticacion)" -ForegroundColor Green
            Write-Host "   Las dependencias estan instaladas correctamente" -ForegroundColor Green
        } elseif ($errorMessage -like "*404*") {
            # 404 puede significar que la app todavia se esta reiniciando
            Write-Host "   Advertencia: La app todavia se esta reiniciando (404)" -ForegroundColor Yellow
            Write-Host "   Espera 1-2 minutos y prueba manualmente las funciones" -ForegroundColor Yellow
        } elseif ($errorMessage -like "*500*" -or $errorMessage -like "*502*" -or $errorMessage -like "*503*") {
            Write-Host "   ERROR: La funcion devolvio un error de servidor" -ForegroundColor Red
            Write-Host "   Esto puede indicar un problema con las dependencias" -ForegroundColor Red
            Write-Host ""
            Write-Host "   Ejecuta este comando para ver los logs:" -ForegroundColor Yellow
            Write-Host "   az functionapp log tail --name $FunctionAppName --resource-group $ResourceGroup" -ForegroundColor Gray
        } else {
            Write-Host "   Advertencia: No se pudo verificar automaticamente" -ForegroundColor Yellow
            Write-Host "   Error: $errorMessage" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "Despliegue finalizado" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Endpoints disponibles:" -ForegroundColor White
    Write-Host "   - PaygoldLink: https://$FunctionAppName.azurewebsites.net/api/PaygoldLink" -ForegroundColor Gray
    Write-Host "   - DecryptAndRedirect: https://$FunctionAppName.azurewebsites.net/api/DecryptAndRedirect" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para ver los logs en tiempo real:" -ForegroundColor White
    Write-Host "   az functionapp log tail --name $FunctionAppName --resource-group $ResourceGroup" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Error durante el despliegue" -ForegroundColor Red
    Write-Host "   Revisa los logs arriba para mas detalles" -ForegroundColor Yellow
    exit 1
}
