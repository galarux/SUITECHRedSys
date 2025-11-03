# 📚 Guía de Desarrollo - SUITECHRedSys

Esta guía contiene todos los pasos necesarios para trabajar con el proyecto **SUITECHRedSys**.

---

## 🐍 Entorno Virtual

### Crear el entorno virtual (ya está creado)
```bash
python -m venv venv
```

### Activar el entorno virtual

**En PowerShell (Windows):**
```powershell
.\venv\Scripts\Activate.ps1
```

**En CMD (Windows):**
```cmd
venv\Scripts\activate.bat
```

**En Linux/Mac:**
```bash
source venv/bin/activate
```

### Desactivar el entorno virtual
```bash
deactivate
```

---

## 📦 Instalación de Dependencias

### Instalar dependencias (con entorno virtual activado)
```bash
pip install -r requirements.txt
```

### Verificar dependencias instaladas
```bash
pip list
```

---

## 🚀 Ejecutar la Azure Function

### Iniciar la función localmente
```bash
func start
```

La función estará disponible en: `http://localhost:7071/api/EncryptData`

---

## 🧪 Probar la Función

**⚠️ IMPORTANTE:** Ejecuta `func start` en una terminal y déjalo corriendo. Luego abre otra terminal para hacer las peticiones.

### Con PowerShell (Recomendado en Windows)

**Comando simple:**
```powershell
Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'
```

**Para ver solo el contenido JSON:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"data":"hola mundo","encryptType":"SHA-256","encryptKey":"clave123"}'; $response.Content
```

**Prueba con SHA-512:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/EncryptData" -Method POST -ContentType "application/json" -Body '{"data":"hola mundo","encryptType":"SHA-512","encryptKey":"clave123"}'; $response.Content
```

### Con curl (PowerShell)
```bash
curl -X POST http://localhost:7071/api/EncryptData -H "Content-Type: application/json" -d '{\"data\":\"hola mundo\",\"encryptType\":\"SHA-256\",\"encryptKey\":\"clave123\"}'
```

### Con curl (CMD o Git Bash)
```bash
curl -X POST http://localhost:7071/api/EncryptData -H "Content-Type: application/json" -d "{\"data\":\"hola mundo\",\"encryptType\":\"SHA-256\",\"encryptKey\":\"clave123\"}"
```

### Con Postman
- **Método:** POST
- **URL:** `http://localhost:7071/api/EncryptData`
- **Headers:** 
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "data": "hola mundo",
  "encryptType": "SHA-256",
  "encryptKey": "clave123"
}
```

---

## 📝 Estructura del Proyecto

```
SUITECHRedSys/
│
├── EncryptData/
│   ├── __init__.py          # Lógica principal de la función
│   └── function.json        # Configuración del trigger HTTP
│
├── utils/
│   └── crypto.py            # Lógica de encriptación
│
├── venv/                    # Entorno virtual (no commitear)
├── requirements.txt         # Dependencias del proyecto
├── host.json               # Configuración del host
├── local.settings.json     # Configuración local (no commitear)
├── GUIA_DESARROLLO.md      # Esta guía
└── SUITECHRedSys_EncryptData.md  # Especificaciones del proyecto
```

---

## 🔧 Comandos Útiles

### Verificar versión de Python
```bash
python --version
```

### Actualizar pip
```bash
python -m pip install --upgrade pip
```

### Ver logs de la función
Cuando ejecutas `func start`, los logs aparecen en la consola.

---

## ⚠️ Notas Importantes

- **local.settings.json** contiene configuraciones sensibles y no debe commitearse a git
- El entorno virtual **venv/** tampoco debe commitearse
- Asegúrate de tener el **Azure Functions Core Tools** instalado para usar `func start`

---

## 📌 Pendientes / Notas Adicionales

- [x] Instalar Azure Functions Core Tools si no está instalado ✅ (Versión 4.4.0 instalada)
- [x] Configurar .gitignore para excluir venv/ y local.settings.json ✅
- [x] Probar la función localmente con `func start` ✅
- [x] Crear README.md ✅

### Nota sobre Azure Functions Core Tools

**Instalación realizada:**
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

**Verificar instalación:**
```bash
func --version
```

Versión instalada: **4.4.0**

---

## 📤 Subir a GitHub

### 1. Preparar los archivos para commit
```bash
git add .
git status  # Verificar qué archivos se van a subir
```

### 2. Hacer el primer commit
```bash
git commit -m "Initial commit: Azure Function EncryptData"
```

### 3. Crear el repositorio en GitHub
1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón "+" (arriba a la derecha) y selecciona "New repository"
3. Nombre del repositorio: `SUITECHRedSys` (o el nombre que prefieras)
4. Descripción: "Azure Function en Python para encriptar datos con SHA-256/SHA-512"
5. Selecciona si quieres que sea público o privado
6. **NO** marques las opciones de "Initialize this repository with a README" (ya tenemos uno)
7. Haz clic en "Create repository"

### 4. Conectar el repositorio local con GitHub
```bash
git remote add origin https://github.com/TU-USUARIO/SUITECHRedSys.git
```

⚠️ Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub.

### 5. Subir el código a GitHub
```bash
git branch -M main
git push -u origin main
```

### Verificar que se subió correctamente
Ve a tu repositorio en GitHub y verifica que todos los archivos estén ahí (excepto venv/ y local.settings.json que están en .gitignore).
