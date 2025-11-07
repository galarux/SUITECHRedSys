from datetime import datetime
from typing import Dict, Any
import uuid

def create_table_entity(
    url_bc: str,
    auth_type: str,
    user: str,
    password: str,
    encrypt_type: str,
    encrypt_key: str,
    error: str = None
) -> Dict[str, Any]:
    """
    Crea una entidad para Azure Table Storage con los datos de la conexión BC.
    
    Args:
        url_bc: URL de BC para reenviar datos después
        auth_type: Tipo de autenticación (Basic o oAuth)
        user: Usuario para autenticación
        password: Contraseña para autenticación
        encrypt_type: Tipo de encriptación usado (SHA-256 o SHA-512)
        encrypt_key: Clave para encriptar/desencriptar
        error: Mensaje de error si hubo alguno (opcional)
    
    Returns:
        Diccionario con la entidad lista para insertar en Table Storage
        Incluye un Id único que se puede usar para buscar después
    """
    now = datetime.utcnow()
    
    # Generar un ID único para esta entrada
    # Usaremos un UUID completo como ID
    unique_id = str(uuid.uuid4())
    
    # PartitionKey: fecha en formato YYYY-MM-DD para facilitar consultas por fecha
    partition_key = now.strftime("%Y-%m-%d")
    
    # RowKey: Usaremos el ID único para facilitar búsquedas posteriores
    # El ID será el que se pase en la URL cuando RedSys llame a DecryptAndRedirect
    row_key = unique_id
    
    entity = {
        "PartitionKey": partition_key,
        "RowKey": row_key,
        "Timestamp": now,
        "Id": unique_id,
        "URLBC": url_bc,
        "AuthType": auth_type,
        "User": user,
        "Pass": password,
        "EncryptType": encrypt_type,
        "EncryptKey": encrypt_key
    }
    
    # Agregar error si existe
    if error:
        entity["Error"] = error
    
    return entity

