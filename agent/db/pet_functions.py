from database.local_db import db

def register_pet(pet_data: dict):
    """Registers a new pet."""
    return db.create_pet(
        client_id=pet_data.get("client_id", 1),
        name=pet_data.get("name", ""),
        pet_type=pet_data.get("type", "dog"),
        breed=pet_data.get("breed", ""),
        age=pet_data.get("age", 0),
        size=pet_data.get("size", "medium"),
        sex=pet_data.get("sex", "male"),
        weight=pet_data.get("weight", 0.0),
        notes=pet_data.get("notes", "")
    )

def get_pets_by_client_id(client_id: int):
    """Returns all pets associated with a given client ID."""
    return db.get_pets_by_client(client_id)

def get_pet_by_id(pet_id: int):
    """Returns a pet by its ID."""
    return db.get_pet_by_id(pet_id)
