import logging
from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from database.services import appointment_service, PetService, ServiceService
from database.schemas import AppointmentCreate

logger = logging.getLogger(__name__)

@tool
def confirm_schedule_tool(
    schedule_info: Annotated[dict, InjectedState("schedule_info")],
    client_info: Annotated[dict, InjectedState("client_info")],
    org_id: Annotated[int, InjectedState("org_id")]
) -> dict:
    """
    Confirms and creates a new appointment for a client.

    Returns:
        dict: {
            "success": bool,
            "data": dict (created appointment details) | None,
            "message": str (error or success message)
        }
    """
    try:
        client_id = client_info.get("id")
        if not client_id:
            return {"success": False, "message": "You need to register the client before."}
            
        service_id = schedule_info.get("service_id")
        pet_id = schedule_info.get("pet_id")
        date = schedule_info.get("date")
        hour = schedule_info.get("hour")

        pet = PetService.get_pet_by_id(pet_id, org_id)
        service = ServiceService.get_service_by_id(service_id, org_id)

        if not pet or not service:
            return {"success": False, "message": "Pet or service not found."}

        pet_type = pet.get("type")
        allowed_pets = service.get("allowed_pets", [])

        if allowed_pets and pet_type not in allowed_pets:
            return {"success": False, "message": "This service does not allow this type of pet."}

        appointment_data = AppointmentCreate(
            client_id=client_id,
            pet_id=pet_id,
            service_id=service_id,
            appointment_date=date,
            appointment_time=hour
        )
        appointment = appointment_service.create_appointment(appointment_data, org_id)
        return {"success": True, "data": dict(appointment)}
    except ValueError as e:
        return {"success": False, "message": str(e)}
    except Exception as e:
        logger.error(f"[confirm_schedule_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Failed to schedule: {str(e)}"}


@tool
def get_schedule_summary_tool(
    schedule_info: Annotated[dict, InjectedState("schedule_info")],
    org_id: Annotated[int, InjectedState("org_id")]
) -> dict:
    """
    Returns a summary of the current schedule being created or confirmed.

    Returns:
        dict: {
            "success": bool,
            "data": {
                "service": dict,
                "pet": dict,
                "date": str,
                "hour": str
            }
        }
    """
    try:
        pet_id = schedule_info.get("pet_id")
        service_id = schedule_info.get("service_id")
        
        if not pet_id or not service_id:
            return {"success": False, "message": "Schedule information is incomplete."}

        pet = PetService.get_pet_by_id(pet_id, org_id)
        service = ServiceService.get_service_by_id(service_id, org_id)

        if not pet or not service:
            return {"success": False, "message": "Pet or service not found."}

        last_schedule = {
            "service": dict(service),
            "pet": dict(pet),
            "date": schedule_info.get("date"),
            "hour": schedule_info.get("hour"),
        }
        return {"success": True, "data": last_schedule}
    except Exception as e:
        logger.error(f"[get_schedule_summary_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error getting schedule summary: {str(e)}"}


confirm_schedule_tools = [confirm_schedule_tool, get_schedule_summary_tool]
