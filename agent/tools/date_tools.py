from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Annotated
from agent.db.appointments_functions import check_availability

@tool
def choose_date_tool(date: str, hour: str) -> dict:
    """
    Selects the desired date and time for the appointment.

    Args:
        date (str): The chosen appointment date (format: YYYY-MM-DD).
        hour (str): The chosen appointment time (format: HH:MM).

    Returns:
        dict: {
            "success": bool,
            "data": {
                "date": str,
                "hour": str
            }
        }
    """
    return {"success": True, "data": {"date": date, "hour": hour}}


@tool
def check_availability_tool(
    org_id: Annotated[int, InjectedState("org_id")],
    service_id: int,
    date: str,
    hour: str,
) -> dict:
    """
    Checks if a specific service is available at a given date and time.

    Args:
        service_id (int): ID of the service to check.
        date (str): Desired appointment date (YYYY-MM-DD).
        hour (str): Desired appointment time (HH:MM).

    Returns:
        dict: {
            "success": bool,
            "message": str
        }
    """
    availability = check_availability(service_id, date, hour, org_id)

    if availability["available"]:
        return {
            "success": True,
            "message": f"Time {hour} on {date} is available for service {service_id}."
        }

    custom_message = availability.get("message", "")
    next_slot = availability.get("next_available_same_day")

    if next_slot:
        msg = f"{custom_message}. The next available time today is {next_slot}."
    elif custom_message:
        msg = custom_message
    else:
        msg = f"Time {hour} on {date} is unavailable."

    return {
        "success": False,
        "message": msg
    }

date_tools = [choose_date_tool, check_availability_tool]
