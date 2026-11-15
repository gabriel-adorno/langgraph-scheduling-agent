from agent.states.all_states import AgentState
from langgraph.types import Overwrite

def reset_state(state: AgentState) -> AgentState:
    schedule_confirmed = state.get("schedule_confirmed", False)

    if schedule_confirmed:
        print("------------- SCHEDULE INFO -------------")
        print(state.get("schedule_info"))
        print("------------- CLIENT INFO -------------")
        print(state.get("client_info"))

        # reseting state
        state["step"] = "CHOOSE_SERVICE"
        state["schedule_confirmed"] = False

        # reseting schedule_info
        if "schedule_info" in state and isinstance(state["schedule_info"], dict):
            state["schedule_info"]["date"] = None
            state["schedule_info"]["hour"] = None
            state["schedule_info"]["service_id"] = None
            state["schedule_info"]["pet_id"] = None

        # has_previous appointments flag
        state["has_previous_appointments"] = True

        # cleaning all the messages
        state["messages"] = Overwrite([])

    return state
