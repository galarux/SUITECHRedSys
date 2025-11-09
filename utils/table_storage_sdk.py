from datetime import datetime
from typing import Any, Dict, Optional
import uuid
import os
import logging
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceNotFoundError

from utils.crypto import encrypt_secret

def get_table_client():
    """
    Obtiene el cliente de Table Storage usando la connection string de Azure.
    """
    # Obtener la connection string de la variable de entorno
    connection_string = os.environ.get("AzureWebJobsStorage")
    
    if not connection_string:
        raise ValueError("AzureWebJobsStorage no está configurado")
    
    table_service = TableServiceClient.from_connection_string(conn_str=connection_string)

    # Asegurar que la tabla existe
    table_service.create_table_if_not_exists(table_name="EncryptDataLogs")

    table_client = table_service.get_table_client(table_name="EncryptDataLogs")
    
    return table_client


def get_entity_by_order_code(order_code: str) -> Optional[Dict[str, Any]]:
    """Recupera una entidad usando el código de pedido almacenado."""

    table_client = get_table_client()

    # Intento 1: nuevo campo Ds_Merchant_Order
    query_filter = "Ds_Merchant_Order eq @order"
    parameters = {"order": order_code}
    results = list(table_client.query_entities(query_filter, parameters=parameters))
    if results:
        return results[0]

    # Intento 2: compatibilidad con registros antiguos (RowKey / Id)
    legacy_filter = "RowKey eq @legacy"
    legacy_params = {"legacy": order_code}
    results = list(table_client.query_entities(legacy_filter, parameters=legacy_params))
    if results:
        return results[0]

    id_filter = "Id eq @identifier"
    id_params = {"identifier": order_code}
    results = list(table_client.query_entities(id_filter, parameters=id_params))
    if results:
        return results[0]

    return None

def save_to_table(
    url_bc: str,
    auth_type: str,
    user: str,
    password: str,
    encrypt_type: str,
    encrypt_key: str,
    ds_merchant_order: str | None = None,
    error: str | None = None,
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
    
    encrypted_password = ""
    pass_encrypted = False
    if password:
        if not encrypt_key:
            raise ValueError("encryptKey es obligatorio para proteger las credenciales.")
        encrypted_password = encrypt_secret(password, encrypt_key)
        pass_encrypted = True
    entity = {
        "PartitionKey": partition_key,
        "RowKey": row_key,
        "Timestamp": now,
        "Id": unique_id,
        "URLBC": url_bc,
        "AuthType": auth_type,
        "User": user,
        "Pass": encrypted_password,
        "PassEncrypted": pass_encrypted,
        "EncryptType": encrypt_type,
        "EncryptKey": encrypt_key
    }

    if ds_merchant_order:
        entity["Ds_Merchant_Order"] = ds_merchant_order
    
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


