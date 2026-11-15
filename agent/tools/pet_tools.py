import logging
from typing import Annotated, Literal
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from database.services import PetService

logger = logging.getLogger(__name__)

@tool
def list_pets_tool(
    client_info: Annotated[dict, InjectedState("client_info")],
    org_id: Annotated[int, InjectedState("org_id")]
) -> dict:
    """
    Retrieves all pets registered for the given client.

    Returns:
        dict: {
            "success": bool,
            "data": list of pets (if successful),
            "message": str (if no pets or error)
        }
    """
    try:
        client_id = client_info.get("id")
        if not client_id:
            return {"success": False, "message": "You need to register the client before."}

        pets = PetService.get_pets_by_client(client_id, org_id)
        if not pets:
            return {"success": False, "message": "This client has no registered pets."}

        formatted = [
            {
                "id": pet["id"],
                "name": pet["name"],
                "type": pet["type"],
                "breed": pet.get("breed", ""),
                "size": pet.get("size", "medium"),
                "sex": pet.get("sex", "male"),
                "age": pet.get("age", 0),
                "weight": pet.get("weight", 0.0),
            }
            for pet in pets
        ]
        return {"success": True, "data": formatted}
    except Exception as e:
        logger.error(f"[list_pets_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error listing pets: {str(e)}"}


@tool
def register_pet_tool(
    client_info: Annotated[dict, InjectedState("client_info")],
    org_id: Annotated[int, InjectedState("org_id")],
    name: str,
    type: Literal["dog", "cat", "rabbit", "bird", "other"],
    breed: str,
    size: Literal["small", "medium", "large"],
    sex: Literal["male", "female"],
    age: int,
    weight: float,
    notes: str = "",
) -> dict:
    """
    Registers a new pet for the given client.

    Args:
        name (str): Name of the pet.
        type (str): Type of the pet (dog, cat, rabbit, bird, other).
        breed (str): Breed of the pet.
        size (str): Size of the pet (small, medium, large).
        sex (str): Sex of the pet (male, female).
        age (int): Age of the pet in years.
        weight (float): Weight of the pet in kilograms.
        notes (str, optional): Additional notes about the pet.

    Returns:
        dict: {
            "success": bool,
            "data": dict with pet info (if successful),
            "message": str (if error)
        }
    """
    try:
        client_id = client_info.get("id")
        if not client_id:
            return {"success": False, "message": "You need to register the client before."}

        pet = PetService.create_pet(
            org_id=org_id,
            client_id=client_id,
            name=name,
            pet_type=type,
            breed=breed,
            age=age,
            size=size,
            sex=sex,
            weight=weight,
            notes=notes
        )

        return {
            "success": True,
            "data": {
                "id": pet["id"],
                "name": pet["name"],
                "type": pet["type"],
                "breed": pet.get("breed", ""),
                "size": pet.get("size", "medium"),
                "sex": pet.get("sex", "male"),
                "age": pet.get("age", 0),
                "weight": pet.get("weight", 0.0)
            }
        }
    except Exception as e:
        logger.error(f"[register_pet_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error registering pet: {str(e)}"}


@tool
def choose_pet_tool(
    pet_id: int,
    client_info: Annotated[dict, InjectedState("client_info")],
    org_id: Annotated[int, InjectedState("org_id")]
) -> dict:
    """
    Selects a pet to be used in the scheduling process.

    Args:
        pet_id (int): ID of the pet to select.

    Returns:
        dict: {
            "success": bool,
            "data": dict with pet info (if successful),
            "message": str (if pet not found)
        }
    """
    try:
        client_id = client_info.get("id")
        if not client_id:
            return {"success": False, "message": "You need to register the client before."}

        pet = PetService.get_pet_by_id(pet_id, org_id)
        if not pet or pet.get("client_id") != client_id:
            return {"success": False, "message": "Pet not found."}

        return {
            "success": True, 
            "data": {
                "id": pet.get("id"),
                "name": pet.get("name"),
                "type": pet.get("type")
            }
        }
    except Exception as e:
        logger.error(f"[choose_pet_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error selecting pet: {str(e)}"}


pet_tools = [list_pets_tool, register_pet_tool, choose_pet_tool]
