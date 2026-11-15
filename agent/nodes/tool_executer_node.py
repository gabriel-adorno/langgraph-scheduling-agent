from langchain_core.messages import ToolMessage
from agent.states.all_states import AgentState
from agent.utils.functions import safe_load_json


def tool_executer(state: AgentState) -> AgentState:
    """Processa a última ToolMessage e atualiza o state do agente."""
    if not state.get("messages"):
        return state

    last = state["messages"][-1]
    if not isinstance(last, ToolMessage):
        return state

    result = safe_load_json(last.content)
    if isinstance(result, dict):
        data = result.get("data", {})
    else:
        data = result

    match last.name:
        case "register_client_tool":
            if isinstance(data, dict):
                state["client_info"]["id"] = data.get("id")
                state["client_info"]["name"] = data.get("name")

        case "get_services_list_tool":
            pass

        case "choose_service_tool":
            if isinstance(data, dict):
                state["schedule_info"]["service_id"] = data.get("id")

        case "list_pets_tool":
            pass

        case "register_pet_tool":
            if isinstance(data, dict):
                state["schedule_info"]["pet_id"] = data.get("id")

        case "choose_pet_tool":
            if isinstance(data, dict):
                state["schedule_info"]["pet_id"] = data.get("id")

        case "choose_date_tool":
            if isinstance(data, dict):
                state["schedule_info"]["date"] = data.get("date")
                state["schedule_info"]["hour"] = data.get("hour")

        case "check_availability_tool":
            pass

        case "confirm_schedule_tool":
            state["schedule_confirmed"] = True

        case "enter_schedule_management_mode":
            state["is_in_schedule_management"] = True

        case "exit_schedule_management_mode":
            state["is_in_schedule_management"] = False

    return state
