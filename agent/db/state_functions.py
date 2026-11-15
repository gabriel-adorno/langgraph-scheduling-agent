from copy import deepcopy
from typing import List, Dict, Any, Optional
import json
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from database.services import (
    ClientService,
    AgentStateService,
    AgentConfigService,
    ClinicConfigService
)
from database.local_db import db


def get_evolution_info(org_id: int = 1) -> Optional[dict]:
    """Returns the Evolution API configuration if present in agent_config."""
    config = db.get_agent_config()
    return config.get("evolution_info")


def serialize_messages(messages: List[BaseMessage]) -> List[dict]:
    """Converte mensagens LangChain para formato JSON"""
    serialized = []
    for msg in messages:
        msg_data = {
            "type": msg.__class__.__name__,
            "content": msg.content,
        }

        if hasattr(msg, "additional_kwargs") and msg.additional_kwargs:
            msg_data["additional_kwargs"] = msg.additional_kwargs

        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            msg_data["tool_calls"] = msg.tool_calls

        if isinstance(msg, ToolMessage):
            if hasattr(msg, "name"):
                msg_data["name"] = msg.name
            if hasattr(msg, "tool_call_id"):
                msg_data["tool_call_id"] = msg.tool_call_id

        serialized.append(msg_data)

    return serialized


def deserialize_messages(data: List[dict]) -> List[BaseMessage]:
    """Converte JSON para mensagens LangChain"""
    messages = []
    for msg_data in data:
        msg_type = msg_data.get("type")
        content = msg_data.get("content")
        additional_kwargs = msg_data.get("additional_kwargs", {})

        if msg_type == "HumanMessage":
            messages.append(HumanMessage(content=content, additional_kwargs=additional_kwargs))
        elif msg_type == "AIMessage":
            tool_calls = msg_data.get("tool_calls", [])
            messages.append(AIMessage(content=content, additional_kwargs=additional_kwargs, tool_calls=tool_calls))
        elif msg_type == "SystemMessage":
            messages.append(SystemMessage(content=content))
        elif msg_type == "ToolMessage":
            messages.append(ToolMessage(content=content, name=msg_data.get("name", ""), tool_call_id=msg_data.get("tool_call_id", "")))

    return messages


def get_client_by_number(user_num: str, org_id: int = 1):
    """Returns client data by phone number from local database."""
    try:
        clean_number = str(user_num).replace("@s.whatsapp.net", "").strip()
        client = db.get_client_by_number(clean_number)
        if client:
            return {
                "id": client["id"],
                "number": clean_number,
                "name": client["name"]
            }
        return None
    except Exception:
        return None


def get_agent_config(org_id: int = 1) -> dict:
    """Returns the agent configuration from local database."""
    try:
        agent_config_row = AgentConfigService.get_agent_config(org_id)
        clinic_config_row = ClinicConfigService.get_clinic_config(org_id)

        clinic_settings = {
            "clinic_name": clinic_config_row.get("clinic_name", "Clínica Veterinária"),
            "working_hours": clinic_config_row.get("working_hours", {}),
            "timezone": clinic_config_row.get("timezone", "America/Sao_Paulo")
        }

        evolution_info = agent_config_row.get("evolution_info")

        config = {
            "name": agent_config_row.get("agent_name", "Júlia"),
            "ai_enabled": agent_config_row.get("is_active", True),
            "personality": {
                "tone": agent_config_row.get("tone", "friendly"),
                "language": agent_config_row.get("language", "pt-BR"),
                "formality": agent_config_row.get("formality", "informal"),
                "emoji_use": agent_config_row.get("emoji_use", "moderate"),
                "audio_use": agent_config_row.get("audio_use", "none"),
                "voice_style": agent_config_row.get("voice_style", "warm"),
                "voice": agent_config_row.get("voice", "alloy")
            },
            "clinic_settings": clinic_settings,
            "technical_settings": {
                "process_audio": agent_config_row.get("process_audio", False),
                "response_delay": agent_config_row.get("response_delay", 0),
                "evolution_info": evolution_info
            }
        }
        return config
    except Exception as e:
        print(f"❌ Error loading agent config: {e}")
        return None


default_history = {
    "messages": [],
    "step": "REGISTER_CLIENT",
    "org_id": 1,
    "client_info": {
        "number": None,
        "id": None,
        "name": None
    },
    "schedule_info": {
        "date": None,
        "hour": None,
        "service_id": None,
        "pet_id": None
    },
    "agent_config": {},
    "schedule_confirmed": False,
    "has_past_appointments": False,
    "has_previous_appointments": False,
    "is_in_schedule_management": False
}


def load_state(org_id: int, user_num: str, agent_config: dict,
               name_suggestion: Optional[str] = None) -> dict:
    """Loads conversation state from local database or creates default."""
    clean_number = str(user_num).replace("@s.whatsapp.net", "").strip()
    state_tuple = AgentStateService.get_agent_state(org_id, clean_number)

    existing_client = get_client_by_number(clean_number, org_id)
    client_id = existing_client["id"] if existing_client else None
    client_name = existing_client["name"] if existing_client else None

    if state_tuple:
        raw_messages = (
            deserialize_messages(state_tuple["messages"])
            if state_tuple.get("messages") else []
        )

        messages = raw_messages[-25:]
        while messages:
            last = messages[-1]
            if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
                messages.pop()
            else:
                break

        state = {
            "messages": messages,
            "step": state_tuple.get("current_step") or state_tuple.get("step", "REGISTER_CLIENT"),
            "org_id": org_id,
            "client_info": {
                "number": clean_number,
                "id": client_id,
                "name": client_name
            },
            "schedule_info": state_tuple.get("schedule_info") or {
                "date": None,
                "hour": None,
                "service_id": None,
                "pet_id": None
            },
            "agent_config": agent_config,
            "schedule_confirmed": state_tuple.get("schedule_confirmed", False),
            "has_previous_appointments": state_tuple.get("has_previous_appointments", False),
            "name_suggestion": state_tuple.get("name_suggestion", name_suggestion),
            "is_in_schedule_management": state_tuple.get("is_in_schedule_management", False)
        }
        return state

    default_state = deepcopy(default_history)
    default_state["client_info"]["number"] = clean_number
    default_state["client_info"]["id"] = client_id
    default_state["client_info"]["name"] = client_name
    default_state["org_id"] = org_id
    default_state["agent_config"] = agent_config
    default_state["name_suggestion"] = name_suggestion

    if client_id:
        default_state["step"] = "CHOOSE_SERVICE"

    return default_state


def save_state(history_updated: dict):
    """Saves conversation state to local storage."""
    org_id = history_updated.get("org_id", 1)
    client_number = history_updated.get("client_info", {}).get("number")
    client_id = history_updated.get("client_info", {}).get("id")

    if client_number:
        client_number = str(client_number).replace("@s.whatsapp.net", "").strip()

    if not client_number:
        print("⚠️ Cannot save state: missing client_number")
        return

    messages_serialized = serialize_messages(history_updated.get("messages", []))

    state_data = {
        "step": history_updated.get("step"),
        "current_step": history_updated.get("step"),
        "schedule_info": history_updated.get("schedule_info", {}),
        "agent_config": history_updated.get("agent_config", {}),
        "messages": messages_serialized,
        "schedule_confirmed": history_updated.get("schedule_confirmed", False),
        "has_previous_appointments": history_updated.get("has_previous_appointments", False),
        "name_suggestion": history_updated.get("name_suggestion"),
        "is_in_schedule_management": history_updated.get("is_in_schedule_management", False)
    }

    try:
        AgentStateService.create_agent_state(org_id, client_number, state_data, client_id)
    except Exception as e:
        print(f"❌ Error saving state: {e}")
