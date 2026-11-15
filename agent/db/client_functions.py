from database.local_db import db

def register_client(client_data: dict):
    """Registers a new client."""
    name = client_data.get("name", "")
    whatsapp_number = client_data.get("number") or client_data.get("whatsapp_number", "")
    return db.create_client(name=name, whatsapp_number=whatsapp_number)

def get_client_by_id(client_id: int):
    """Finds a client by its ID."""
    return db.get_client_by_id(client_id)
