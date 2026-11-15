import logging
from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from database.services import ClientService
from database.schemas import ClientCreate

logger = logging.getLogger(__name__)

@tool
def register_client_tool(
    name: str,
    org_id: Annotated[int, InjectedState("org_id")],
    client_info: Annotated[dict, InjectedState("client_info")]
) -> dict:
    """
    Registers a new client in the system.

    Args:
        name (str): The client's name.

    Returns:
        dict: {
            "success": bool,
            "data": dict (client information)
        }
    """
    try:
        whatsapp_number = client_info.get("number")
        if not whatsapp_number:
            return {"success": False, "message": "WhatsApp number not found."}

        clean_number = str(whatsapp_number).replace("@s.whatsapp.net", "").strip()
        client = ClientService.create_client(org_id=org_id, name=name, whatsapp_number=clean_number)

        return {
            "success": True,
            "data": {
                "id": client["id"],
                "name": client["name"],
                "whatsapp_number": client["whatsapp_number"]
            }
        }
    except Exception as e:
        logger.error(f"[register_client_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error registering client: {str(e)}"}

client_tools = [register_client_tool]
