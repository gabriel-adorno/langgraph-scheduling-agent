from database.local_db import db

def get_service_list():
    """Returns the list of available services."""
    return db.get_services()

def get_service_by_id(service_id: int):
    """Returns a service by its ID."""
    return db.get_service_by_id(service_id)
