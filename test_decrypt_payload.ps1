# Script para probar DecryptAndRedirect y ver el payload enviado
# Uso: .\test_decrypt_payload.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$FunctionUrl = "https://suitechredsys.azurewebsites.net/api/decryptandredirect"
)

Write-Host "🧪 Probando DecryptAndRedirect para ver el payload..." -ForegroundColor Cyan
Write-Host ""

# Necesitarás generar estos valores con el script generate_redsys_payload.py
# Este es un ejemplo - DEBES usar valores reales de una transacción de prueba

$body = @{
    Ds_SignatureVersion = "HMAC_SHA256_V1"
    Ds_MerchantParameters = "TU_MERCHANT_PARAMETERS_BASE64_AQUI"
    Ds_Signature = "TU_SIGNATURE_AQUI"
} | ConvertTo-Json

Write-Host "📤 Enviando petición a DecryptAndRedirect..." -ForegroundColor Yellow
Write-Host "URL: $FunctionUrl" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest `
        -Uri $FunctionUrl `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing `
        -ErrorAction Stop
    
    Write-Host "✅ Respuesta recibida (HTTP $($response.StatusCode))" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Respuesta completa:" -ForegroundColor Cyan
    $responseJson = $response.Content | ConvertFrom-Json
    $responseJson | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "🔍 Payload enviado a Business Central:" -ForegroundColor Cyan
    if ($responseJson.bcCall -and $responseJson.bcCall.payload) {
        Write-Host ""
        Write-Host "Estructura del payload:" -ForegroundColor Yellow
        $responseJson.bcCall.payload | ConvertTo-Json -Depth 10
        
        # Verificar si paymentInfo es un string
        if ($responseJson.bcCall.payload.paymentInfo) {
            $paymentInfo = $responseJson.bcCall.payload.paymentInfo
            Write-Host ""
            if ($paymentInfo -is [string]) {
                Write-Host "✅ CONFIRMADO: paymentInfo es un STRING (campo único)" -ForegroundColor Green
                Write-Host ""
                Write-Host "Contenido deserializado de paymentInfo:" -ForegroundColor Cyan
                $paymentInfo | ConvertFrom-Json | ConvertTo-Json -Depth 5
            } else {
                Write-Host "⚠️  paymentInfo es un OBJETO (campos separados)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "⚠️  No se encontró información de bcCall en la respuesta" -ForegroundColor Yellow
    }
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "❌ Error: HTTP $statusCode" -ForegroundColor Red
    Write-Host ""
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Respuesta del servidor:" -ForegroundColor Yellow
        $responseBody | ConvertFrom-Json | ConvertTo-Json -Depth 10
    } else {
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "💡 Nota: Para generar valores válidos de prueba, usa:" -ForegroundColor Cyan
Write-Host "   python tools/generate_redsys_payload.py ORDER123 YOUR_KEY" -ForegroundColor Gray

