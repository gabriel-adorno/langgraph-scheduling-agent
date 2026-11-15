import logging
from typing import Optional, Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from database.services import appointment_service
from database.schemas import AppointmentUpdate

logger = logging.getLogger(__name__)

@tool
def get_past_schedules_list_tool(
    client_info: Annotated[dict, InjectedState("client_info")],
    org_id: Annotated[int, InjectedState("org_id")]
):
    """
    Retrieves all past appointments for a given client.

    Returns:
        list: A list of past schedules or an empty list if none are found.
    """
    try:
        client_id = client_info.get("id")
        if not client_id:
            return {"success": False, "message": "You need to register the client before."}

        result = appointment_service.get_appointments_by_org(org_id=org_id)
        appointments = [a for a in result.get("appointments", []) if a.get("client_id") == client_id]

        if not appointments:
            return {"success": False, "message": "No appointments found."}

        formatted = [
            {
                "id": appt["id"],
                "service_id": appt.get("service_id"),
                "pet_id": appt.get("pet_id"),
                "date": appt.get("appointment_date"),
                "hour": appt.get("appointment_time"),
                "status": appt.get("status")
            }
            for appt in appointments
        ]
        return {"success": True, "data": formatted}
    except Exception as e:
        logger.error(f"[get_past_schedules_list_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error listing appointments: {str(e)}"}


@tool 
def cancel_schedule_tool(
    appointment_id: int,
    org_id: Annotated[int, InjectedState("org_id")]
):
    """
    Cancels an existing appointment.

    Args:
        appointment_id (int): The appointment's unique identifier.

    Returns:
        dict: A structured response with success status and message.
    """
    try:
        appointment_data = AppointmentUpdate(status="CANCELLED")
        appointment = appointment_service.update_appointment(
            appointment_id=appointment_id,
            appointment=appointment_data,
            org_id=org_id
        )
        if not appointment:
            return {"success": False, "message": "This appointment_id is invalid."}

        return {
            "success": True,
            "data": dict(appointment),
            "message": "Schedule cancelled successfully."
        }
    except Exception as e:
        logger.error(f"[cancel_schedule_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error cancelling appointment: {str(e)}"}


@tool
def edit_schedule_tool(
    schedule_id: int,
    org_id: Annotated[int, InjectedState("org_id")],
    date: Optional[str] = None,
    hour: Optional[str] = None,
    pet_id: Optional[int] = None,
    service_id: Optional[int] = None
):
    """
    Edits an existing appointment.

    Args:
        schedule_id (int): The appointment's unique identifier.
        date (str, optional): New date for the appointment.
        hour (str, optional): New hour for the appointment.
        pet_id (int, optional): Updated pet ID.
        service_id (int, optional): Updated service ID.

    Returns:
        dict: A structured response with success status and updated data.
    """
    try:
        update_data = {}
        if date:
            update_data["appointment_date"] = date
        if hour:
            update_data["appointment_time"] = hour
        if pet_id:
            update_data["pet_id"] = pet_id
        if service_id:
            update_data["service_id"] = service_id

        if not update_data:
            return {"success": False, "message": "No fields to update."}

        appointment_data = AppointmentUpdate(**update_data)
        appointment = appointment_service.update_appointment(
            appointment_id=schedule_id,
            appointment=appointment_data,
            org_id=org_id
        )

        if appointment:
            return {
                "success": True,
                "data": dict(appointment),
                "message": f"Schedule {schedule_id} updated successfully."
            }
        else:
            return {
                "success": False,
                "message": f"Schedule {schedule_id} not found."
            }
    except Exception as e:
        logger.error(f"[edit_schedule_tool] Error: {e}", exc_info=True)
        return {"success": False, "message": f"Error updating appointment: {str(e)}"}


schedule_tools = [get_past_schedules_list_tool, cancel_schedule_tool, edit_schedule_tool]
