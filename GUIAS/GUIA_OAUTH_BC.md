# Guía Integración OAuth2 Business Central

## Paso 1: Registro en Entra ID

- Portal Entra ID → `Registros de aplicaciones` → `Nuevo registro`.
- Tipo de cuenta compatible: `Solo cuentas en este directorio` (single tenant).
- Crear un secreto en `Certificados y secretos`. Guardar `client_id`, `tenant_id`, el **valor** del secreto y su caducidad.

## Paso 2: Configurar permisos de API

- `Permisos de API` → `Agregar permiso` → `Dynamics 365 Business Central`.
- Seleccionar `Application` y añadir como mínimo `API.ReadWrite.All` (añadir `Automation.ReadWrite.All` si aplica).
- Quitar permisos por defecto que no se usen y pulsar `Conceder consentimiento de administrador`.

## Paso 3: Configurar redirect URI

- En `Autenticación`, agregar plataforma `Aplicación web`.
- Definir redirect URI `https://businesscentral.dynamics.com/OAuthLanding.htm`.

## Paso 4: Registrar la aplicación en Business Central

- Entrar al entorno de Business Central (cliente web) con usuario administrador.
- Buscar la página `Azure Active Directory Applications`.
- Crear un registro nuevo pegando el `Application (client) ID`, asignar nombre y empresa (o activar “Allow application to act on behalf of any company”).
- Asignar el conjunto de permisos (por ejemplo `D365 BUS FULL ACCESS`).
- Cambiar el estado a `Activo`; iniciar sesión cuando lo solicite y conceder consentimiento.

## Paso 5: Prueba en Postman

### Variables de entorno

- Crear un entorno con variables: `tenant_id`, `client_id`, `client_secret`, `environment_name`.

### Solicitud de token

- `POST https://login.microsoftonline.com/{{tenant_id}}/oauth2/v2.0/token`
- Body `x-www-form-urlencoded`:
  - `grant_type=client_credentials`
  - `client_id={{client_id}}`
  - `client_secret={{client_secret}}`
  - `scope=https://api.businesscentral.dynamics.com/.default`

### Llamada de verificación

- `GET https://api.businesscentral.dynamics.com/v2.0/{{tenant_id}}/{{environment_name}}/api/v2.0/companies`
- Autenticación `Bearer` con el `access_token` obtenido.
- Validar respuesta 200 con la lista de compañías.

## Siguientes pasos

- Almacenar `tenant_id`, `client_id` y secreto en un almacén seguro (Azure Key Vault, configuración de Functions).
- Implementar PoC en Azure Functions reutilizando el flujo `client_credentials`.

