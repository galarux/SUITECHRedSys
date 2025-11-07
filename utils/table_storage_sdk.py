from datetime import datetime
from typing import Dict, Any
import uuid
import os
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceNotFoundError

def get_table_client():
    """
    Obtiene el cliente de Table Storage usando la connection string de Azure.
    """
    # Obtener la connection string de la variable de entorno
    connection_string = os.environ.get("AzureWebJobsStorage")
    
    if not connection_string:
        raise ValueError("AzureWebJobsStorage no está configurado")
    
    table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service.get_table_client(table_name="EncryptDataLogs")
    
    # Crear la tabla si no existe
    try:
        table_client.create_table()
    except Exception:
        # La tabla ya existe, ignorar el error
        pass
    
    return table_client

def save_to_table(
    url_bc: str,
    auth_type: str,
    user: str,
    password: str,
    encrypt_type: str,
    encrypt_key: str,
    error: str = None
) -> str:
    """
    Guarda una entidad en Azure Table Storage usando el SDK directamente.
    
    Args:
        url_bc: URL de BC para reenviar datos después
        auth_type: Tipo de autenticación (Basic o oAuth)
        user: Usuario para autenticación
        password: Contraseña para autenticación
        encrypt_type: Tipo de encriptación usado (SHA-256 o SHA-512)
        encrypt_key: Clave para encriptar/desencriptar
        error: Mensaje de error si hubo alguno (opcional)
    
    Returns:
        ID único generado para la entidad
    """
    now = datetime.utcnow()
    
    # Generar un ID único para esta entrada
    unique_id = str(uuid.uuid4())
    
    # PartitionKey: fecha en formato YYYY-MM-DD para facilitar consultas por fecha
    partition_key = now.strftime("%Y-%m-%d")
    
    # RowKey: Usaremos el ID único para facilitar búsquedas posteriores
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
    
    try:
        table_client = get_table_client()
        table_client.upsert_entity(entity=entity)
        return unique_id
    except Exception as e:
        # Si falla, devolver None pero no romper la función
        import logging
        logging.error(f"Error al guardar en tabla: {str(e)}")
        return None

