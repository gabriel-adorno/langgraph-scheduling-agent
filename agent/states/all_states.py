from typing import Annotated, Sequence, TypedDict, Optional, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

class PersonalitySettings(TypedDict):
    tone: str       
    language: str           
    formality: str          
    emoji_use: str          
    voice_style: str        

class ClinicSettings(TypedDict):
    clinic_name: str
    working_hours: dict
    timezone: str

class AgentConfig(TypedDict):
    name: str
    personality: PersonalitySettings
    clinic_settings: ClinicSettings

class ClientInfo(TypedDict):
    number: str
    id: int
    name: str

class ScheduleInfo(TypedDict):
    date: str
    hour: str
    service_id: int
    pet_id: int

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    step: str
    org_id: int
    client_info: ClientInfo
    schedule_info: ScheduleInfo
    agent_config: AgentConfig
    schedule_confirmed: bool
    has_previous_appointments: bool
    name_suggestion: str | None
    is_in_schedule_management: Optional[bool]

class AgentAction(BaseModel):      
    mode: Literal["text", "audio"]   
    reply_to: Optional[str]
    content: str

class DBMessage(BaseModel):
    id: str     
    mode: Literal["text", "audio", "image"]            
    reply_to: Optional[str]
    content: str
