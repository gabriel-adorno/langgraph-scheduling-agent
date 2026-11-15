from typing import Optional, List, Union

try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self, **kwargs):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class ClientCreate(BaseModel):
    name: str
    whatsapp_number: str

class AppointmentCreate(BaseModel):
    client_id: int
    pet_id: int
    service_id: Union[int, List[int]]
    appointment_date: str
    appointment_time: str

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    pet_id: Optional[int] = None
    service_id: Optional[Union[int, List[int]]] = None
