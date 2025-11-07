# 📊 Guía para Ver Logs en Azure Portal

Esta guía explica cómo ver los logs de la función `EncryptData` en Azure Portal para identificar errores.

---

## 🎯 Método 1: Log Stream (Tiempo Real) - Recomendado

### Paso 1: Acceder a Log Stream
1. En Azure Portal, ve a tu **Function App** `suitechredsys`
2. En el menú lateral izquierdo, busca **"Log stream"** o **"Secuencia de registro"**
3. Haz clic en **"Log stream"**

### Paso 2: Ver los Logs
- Verás los logs en tiempo real
- Si hay errores, aparecerán en rojo
- Los logs mostrarán cualquier error al iniciar la función

### Paso 3: Probar la Función
1. Deja la ventana de Log Stream abierta
2. En otra pestaña o Postman, haz una llamada a la función:
   ```
   POST https://suitechredsys.azurewebsites.net/api/EncryptData
   ```
3. Vuelve a Log Stream y verás los logs de la llamada

---

## 🎯 Método 2: Monitor (Logs Históricos)

### Paso 1: Acceder a Monitor
1. En Azure Portal, ve a tu **Function App** `suitechredsys`
2. En el menú lateral, busca **"Functions"** o **"Funciones"**
3. Haz clic en **"Functions"**
4. Haz clic en la función **"EncryptData"**
5. En el menú de la función, busca **"Monitor"** o **"Supervisar"**
6. Haz clic en **"Monitor"**

### Paso 2: Ver Invocaciones
1. Verás una lista de invocaciones de la función
2. Si hay errores, aparecerán con un icono rojo o estado "Failed"
3. Haz clic en una invocación para ver los detalles

### Paso 3: Ver Detalles del Error
1. Haz clic en una invocación con error
2. Verás los detalles del error:
   - **Status**: Código de estado (404, 500, etc.)
   - **Exception**: Mensaje de error
   - **Logs**: Logs completos de la ejecución

---

## 🎯 Método 3: Application Insights (Si está habilitado)

### Paso 1: Acceder a Application Insights
1. En Azure Portal, ve a tu **Function App** `suitechredsys`
2. En el menú lateral, busca **"Application Insights"**
3. Haz clic en **"Application Insights"**

### Paso 2: Ver Logs
1. En Application Insights, ve a **"Logs"** o **"Registros"**
2. Puedes hacer consultas para ver errores:
   ```kusto
   traces
   | where message contains "error" or message contains "Error" or message contains "Exception"
   | order by timestamp desc
   ```

---

## 🎯 Método 4: Logs de la Function App

### Paso 1: Acceder a Logs
1. En Azure Portal, ve a tu **Function App** `suitechredsys`
2. En el menú lateral, busca **"Logs"** o **"Registros"**
3. Haz clic en **"Logs"**

### Paso 2: Ver Logs del Sistema
- Verás logs del sistema de Azure Functions
- Busca errores relacionados con el inicio de la función
- Busca mensajes que contengan "EncryptData" o "error"

---

## 🔍 Qué Buscar en los Logs

### Errores Comunes:

1. **Error de Importación:**
   ```
   ModuleNotFoundError: No module named 'utils'
   ```
   - **Solución**: Verificar que `utils/__init__.py` existe

2. **Error de Binding:**
   ```
   Error binding parameter 'outputTable'
   ```
   - **Solución**: El binding de Table Storage puede tener problemas

3. **Error de Inicio:**
   ```
   Function 'EncryptData' failed to load
   ```
   - **Solución**: Hay un error en el código que impide que la función se registre

4. **Error de Conexión:**
   ```
   Unable to connect to storage account
   ```
   - **Solución**: Verificar la configuración de `AzureWebJobsStorage`

---

## 📝 Pasos Rápidos para Ver Logs Ahora

1. **En Azure Portal:**
   - Ve a `suitechredsys` → **"Log stream"** (o **"Secuencia de registro"**)
   - Deja la ventana abierta

2. **Haz una llamada de prueba:**
   - En Postman o PowerShell, llama a la función
   - Vuelve a Log Stream y verás los logs

3. **Busca errores:**
   - Busca líneas en rojo o que contengan "error", "Error", "Exception"
   - Copia el mensaje de error completo

---

## 🆘 Si No Ves Logs

### Verificar Configuración:
1. Ve a **"Configuration"** o **"Configuración"** en la Function App
2. Verifica que **"Application Insights"** esté habilitado (opcional pero recomendado)
3. Verifica que **"Always On"** esté habilitado si usas un plan de App Service (no aplica para Consumption)

### Alternativa: Usar Azure CLI
```powershell
# Ver logs recientes
az functionapp log tail --name suitechredsys --resource-group rg-suitech-redsys
```

---

## 📸 Captura de Pantalla

Si puedes, haz una captura de pantalla de:
1. La ventana de Log Stream
2. Cualquier error que aparezca
3. Los detalles de una invocación fallida

Esto me ayudará a identificar el problema exacto.

