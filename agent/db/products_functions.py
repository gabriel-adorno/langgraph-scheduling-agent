from database.local_db import db

def search_products(product_name: str):
    """Returns the list of products by its name."""
    return db.search_products(product_name)
