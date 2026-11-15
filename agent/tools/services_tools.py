import logging
from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from database.services import ServiceService

logger = logging.getLogger(__name__)

@tool
def get_services_list_tool(
        org_id: Annotated[int, InjectedState("org_id")]) -> dict:
    """
    Retrieves the list of available services for the organization.

    Returns:
        dict: A structured response containing:
            - success (bool): Whether the operation was successful.
            - data (list[dict] | None): List of services with their ID, name, and duration.
            - message (str): A message describing the result or error.
    """
    try:
        result = ServiceService.get_services_by_org(org_id=org_id, page=1, page_size=100)
        services = result.get("services", [])

        if not services:
            return {"success": False, "message": "No services available at the moment."}

        formatted = [{
            "id": srv["id"],
            "price": float(srv["price"]) if srv.get("price") else 0.0,
            "name": srv["name"],
            "duration": srv.get("duration_minutes", 30),
            "allowed_pets": srv.get("allowed_pets", []),
            "description": srv.get("description", "")
        } for srv in services]

        return {"success": True, "data": formatted}
    except Exception as e:
        logger.error(f"[get_services_list_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error listing services: {str(e)}"}


@tool
def choose_service_tool(
        service_id: int, org_id: Annotated[int, InjectedState("org_id")]) -> dict:
    """
    Selects a service for the appointment.

    ⚠️ This tool should only be used **after the user has explicitly confirmed**
    which service they want to schedule. Do NOT call this tool immediately when
    the user mentions a service.

    Args:
        service_id (int): The unique identifier of the selected service.

    Returns:
        dict: A structured response containing:
            - success (bool): Whether the selection was successful.
            - data (dict | None): The selected service information.
            - message (str): A message describing the result or error.
    """
    try:
        service = ServiceService.get_service_by_id(service_id, org_id)
        if not service:
            return {"success": False, "message": "Service not found."}

        return {
            "success": True, 
            "data": {
                "id": service.get("id"),
                "name": service.get("name"),
                "duration_minutes": service.get("duration_minutes", 30),
                "price": float(service.get("price", 0))
            }
        }
    except Exception as e:
        logger.error(f"[choose_service_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error selecting service: {str(e)}"}


services_tools = [get_services_list_tool, choose_service_tool]
