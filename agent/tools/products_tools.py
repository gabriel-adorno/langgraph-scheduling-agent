from langchain_core.tools import tool
from agent.db.products_functions import search_products

@tool
def search_products_tool(product_name: str):
    """Search for products by name and suggest visiting the store if none are found."""
    products = search_products(product_name)

    if products:
        return {
            "success": True,
            "data": products,
            "message": f"{len(products)} product(s) found matching '{product_name}'. Please visit the store to purchase it."
        }
    else:
        return {
            "success": False,
            "message": f"No products found matching '{product_name}'. You can visit the store to check for availability."
        }

products_tools = [search_products_tool]
