import json
from langchain_core.messages import SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

from agent.states.all_states import AgentState, DBMessage
from agent.utils.prompts import get_prompt
from agent.utils.functions import parse_agent_action, get_llm_model
from agent.db.whatsapp_functions import send_message
from database.services import AgentConfigService
from agent.tools.all_tools import all_tools


def agent(state: AgentState) -> AgentState:
    client_info = state.get("client_info") or {}
    user_num = client_info.get("number")
    agent_config = state.get("agent_config") or {}
    tech_settings = agent_config.get("technical_settings") or {}
    evolution_info = tech_settings.get("evolution_info")
    org_id = state.get("org_id", 1)

    api_key = AgentConfigService.get_effective_openai_key(org_id)
    system_prompt = SystemMessage(content=get_prompt(state))

    llm = ChatOpenAI(model=get_llm_model(), api_key=api_key).bind_tools(all_tools)
    response = llm.invoke([system_prompt] + list(state["messages"]))

    print(f"📍 ETAPA ATUAL: {state.get('step')}")

    if response.content:
        parsed = parse_agent_action(response.content, api_key)
        action = json.loads(parsed.content) if isinstance(parsed.content, str) else parsed.content

        sent_id = send_message(org_id, action, evolution_info, user_num)
        if not sent_id:
            return state

        db_message = DBMessage(
            id=sent_id,
            mode=action.get("mode", "text"),
            reply_to=action.get("reply_to"),
            content=action.get("content", "")
        )

        ai_llm_message = AIMessage(
            content=json.dumps(db_message.model_dump(), ensure_ascii=False),
            additional_kwargs={"message_type": "agent"}
        )

        state["messages"].append(ai_llm_message)
        return state
    else:
        if hasattr(response, "tool_calls") and response.tool_calls:
            print("🛠️ TOOL CALLS:", [tc["name"] for tc in response.tool_calls])
        state["messages"].append(response)

    return state
