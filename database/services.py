import os
from typing import Optional, List, Dict, Any, Union
from datetime import date, time
from .local_db import db
from .schemas import ClientCreate, AppointmentCreate, AppointmentUpdate

class ClientService:
    @staticmethod
    def get_clients_by_org(org_id: int = 1, search: Optional[str] = None) -> Dict[str, Any]:
        clients = db.get_clients(search=search)
        return {"clients": clients, "total": len(clients)}

    @staticmethod
    def get_client_by_id(client_id: int, org_id: int = 1) -> Optional[Dict[str, Any]]:
        return db.get_client_by_id(client_id)

    @staticmethod
    def create_client(org_id: int = 1, name: str = "", whatsapp_number: str = "") -> Dict[str, Any]:
        return db.create_client(name=name, whatsapp_number=whatsapp_number)


class PetService:
    @staticmethod
    def get_pets_by_client(client_id: int, org_id: int = 1) -> List[Dict[str, Any]]:
        return db.get_pets_by_client(client_id)

    @staticmethod
    def get_pet_by_id(pet_id: int, org_id: int = 1) -> Optional[Dict[str, Any]]:
        return db.get_pet_by_id(pet_id)

    @staticmethod
    def create_pet(org_id: int = 1, client_id: int = 0, name: str = "",
                   pet_type: str = "dog", breed: str = "", age: int = 0,
                   size: str = "medium", sex: str = "male", weight: float = 0.0,
                   notes: str = "") -> Dict[str, Any]:
        return db.create_pet(
            client_id=client_id,
            name=name,
            pet_type=pet_type,
            breed=breed,
            age=age,
            size=size,
            sex=sex,
            weight=weight,
            notes=notes
        )


class ServiceService:
    @staticmethod
    def get_services_by_org(org_id: int = 1, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        services = db.get_services()
        return {"services": services, "total": len(services)}

    @staticmethod
    def get_service_by_id(service_id: int, org_id: int = 1) -> Optional[Dict[str, Any]]:
        return db.get_service_by_id(service_id)


class AppointmentService:
    @staticmethod
    def get_appointments_by_org(org_id: int = 1, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        appts = db.get_appointments()
        return {"appointments": appts, "total": len(appts)}

    @staticmethod
    def create_appointment(appointment_data: Union[AppointmentCreate, dict], org_id: int = 1) -> Dict[str, Any]:
        if isinstance(appointment_data, AppointmentCreate):
            data = appointment_data.model_dump()
        else:
            data = appointment_data

        return db.create_appointment(
            client_id=data["client_id"],
            pet_id=data["pet_id"],
            service_id=data["service_id"],
            appointment_date=str(data["appointment_date"]),
            appointment_time=str(data["appointment_time"])
        )

    @staticmethod
    def update_appointment(appointment_id: int, appointment: Union[AppointmentUpdate, dict], org_id: int = 1) -> Optional[Dict[str, Any]]:
        if isinstance(appointment, AppointmentUpdate):
            data = appointment.model_dump(exclude_unset=True)
        else:
            data = appointment

        return db.update_appointment(appointment_id, **data)


# Module-level instance to match `from ... import appointment_service`
appointment_service = AppointmentService()


class ClinicConfigService:
    @staticmethod
    def get_clinic_config(org_id: int = 1) -> Dict[str, Any]:
        return db.get_clinic_config()

    @staticmethod
    def update_clinic_config(org_id: int = 1, **kwargs) -> Dict[str, Any]:
        return db.update_clinic_config(**kwargs)


class BlockedScheduleService:
    @staticmethod
    def get_blocked_days(org_id: int = 1, date_val: Optional[Union[str, date]] = None) -> List[Dict[str, Any]]:
        return db.get_blocked_days(date_val=date_val)

    @staticmethod
    def get_blocked_times(org_id: int = 1, date_val: Optional[Union[str, date]] = None) -> List[Dict[str, Any]]:
        return db.get_blocked_times(date_val=date_val)


class AgentConfigService:
    @staticmethod
    def get_agent_config(org_id: int = 1) -> Dict[str, Any]:
        return db.get_agent_config()

    @staticmethod
    def get_effective_openai_key(org_id: int = 1) -> str:
        # Prioritize OPENAI_API_KEY from environment/.env
        key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_TRIAL")
        if not key:
            cfg = db.get_agent_config()
            key = cfg.get("openai_api_key")
        if not key:
            raise ValueError("OPENAI_API_KEY não configurada no arquivo .env ou no config local.")
        return key


class AgentStateService:
    @staticmethod
    def get_agent_state(org_id: int = 1, client_number: str = "") -> Optional[Dict[str, Any]]:
        return db.get_agent_state(client_number)

    @staticmethod
    def create_agent_state(org_id: int = 1, client_number: str = "", state_data: dict = None, client_id: Optional[int] = None):
        db.save_agent_state(client_number, state_data or {}, client_id=client_id)

    @staticmethod
    def update_agent_state(org_id: int = 1, client_number: str = "", state_data: dict = None, client_id: Optional[int] = None):
        db.save_agent_state(client_number, state_data or {}, client_id=client_id)
