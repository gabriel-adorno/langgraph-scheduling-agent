import os
import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, time

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class LocalDB:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LocalDB, cls).__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.clients_file = DATA_DIR / "clients.json"
        self.pets_file = DATA_DIR / "pets.json"
        self.services_file = DATA_DIR / "services.json"
        self.appointments_file = DATA_DIR / "appointments.json"
        self.products_file = DATA_DIR / "products.json"
        self.clinic_config_file = DATA_DIR / "clinic_config.json"
        self.agent_config_file = DATA_DIR / "agent_config.json"
        self.blocked_schedules_file = DATA_DIR / "blocked_schedules.json"
        self.conversations_file = DATA_DIR / "conversations.json"

    def _read_json(self, file_path: Path, default_val: Any) -> Any:
        with self._lock:
            if not file_path.exists():
                self._write_json(file_path, default_val)
                return default_val
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao ler {file_path}: {e}")
                return default_val

    def _write_json(self, file_path: Path, data: Any):
        with self._lock:
            temp_path = file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            temp_path.replace(file_path)

    # ==========================
    # CLIENTS
    # ==========================
    def get_clients(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        clients = self._read_json(self.clients_file, [])
        if search:
            s = str(search).lower().strip()
            return [
                c for c in clients 
                if s in str(c.get("name", "")).lower() 
                or s in str(c.get("whatsapp_number", "")).lower()
                or s in str(c.get("id", ""))
            ]
        return clients

    def get_client_by_id(self, client_id: int) -> Optional[Dict[str, Any]]:
        for client in self.get_clients():
            if client["id"] == client_id:
                return dict(client)
        return None

    def get_client_by_number(self, whatsapp_number: str) -> Optional[Dict[str, Any]]:
        clean = str(whatsapp_number).replace("@s.whatsapp.net", "").strip()
        for client in self.get_clients():
            client_num = str(client.get("whatsapp_number", "")).replace("@s.whatsapp.net", "").strip()
            if client_num == clean:
                return dict(client)
        return None

    def create_client(self, name: str, whatsapp_number: str) -> Dict[str, Any]:
        with self._lock:
            clients = self._read_json(self.clients_file, [])
            clean_num = str(whatsapp_number).replace("@s.whatsapp.net", "").strip()
            
            # Verificar se já existe
            for c in clients:
                if str(c.get("whatsapp_number", "")).replace("@s.whatsapp.net", "").strip() == clean_num:
                    c["name"] = name
                    self._write_json(self.clients_file, clients)
                    return dict(c)

            new_id = max([c["id"] for c in clients], default=0) + 1
            new_client = {
                "id": new_id,
                "name": name,
                "whatsapp_number": clean_num
            }
            clients.append(new_client)
            self._write_json(self.clients_file, clients)
            return dict(new_client)

    # ==========================
    # PETS
    # ==========================
    def get_pets(self) -> List[Dict[str, Any]]:
        return self._read_json(self.pets_file, [])

    def get_pets_by_client(self, client_id: int) -> List[Dict[str, Any]]:
        return [p for p in self.get_pets() if p.get("client_id") == client_id]

    def get_pet_by_id(self, pet_id: int) -> Optional[Dict[str, Any]]:
        for pet in self.get_pets():
            if pet.get("id") == pet_id:
                return dict(pet)
        return None

    def create_pet(self, client_id: int, name: str, pet_type: str, breed: str,
                   age: int, size: str, sex: str, weight: float, notes: str = "") -> Dict[str, Any]:
        with self._lock:
            pets = self._read_json(self.pets_file, [])
            new_id = max([p["id"] for p in pets], default=0) + 1
            new_pet = {
                "id": new_id,
                "client_id": client_id,
                "name": name,
                "type": pet_type,
                "breed": breed,
                "age": age,
                "size": size,
                "sex": sex,
                "weight": weight,
                "notes": notes
            }
            pets.append(new_pet)
            self._write_json(self.pets_file, pets)
            return dict(new_pet)

    # ==========================
    # SERVICES
    # ==========================
    def get_services(self) -> List[Dict[str, Any]]:
        return self._read_json(self.services_file, [])

    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        for s in self.get_services():
            if s.get("id") == service_id:
                return dict(s)
        return None

    # ==========================
    # APPOINTMENTS
    # ==========================
    def get_appointments(self) -> List[Dict[str, Any]]:
        return self._read_json(self.appointments_file, [])

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        for a in self.get_appointments():
            if a.get("id") == appointment_id:
                return dict(a)
        return None

    def create_appointment(self, client_id: int, pet_id: int, service_id: Union[int, List[int]],
                           appointment_date: str, appointment_time: str,
                           duration_minutes: Optional[int] = None) -> Dict[str, Any]:
        with self._lock:
            appointments = self._read_json(self.appointments_file, [])
            service_ids = [service_id] if isinstance(service_id, int) else service_id
            
            if duration_minutes is None:
                duration_minutes = 0
                for sid in service_ids:
                    srv = self.get_service_by_id(sid)
                    if srv:
                        duration_minutes += srv.get("duration_minutes", 30)

            new_id = max([a["id"] for a in appointments], default=0) + 1
            new_appointment = {
                "id": new_id,
                "client_id": client_id,
                "pet_id": pet_id,
                "service_id": service_ids[0] if service_ids else 1,
                "service_ids": service_ids,
                "appointment_date": str(appointment_date),
                "appointment_time": str(appointment_time),
                "duration_minutes": duration_minutes,
                "status": "SCHEDULED"
            }
            appointments.append(new_appointment)
            self._write_json(self.appointments_file, appointments)
            return dict(new_appointment)

    def update_appointment(self, appointment_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        with self._lock:
            appointments = self._read_json(self.appointments_file, [])
            for appt in appointments:
                if appt["id"] == appointment_id:
                    for k, v in kwargs.items():
                        if v is not None:
                            appt[k] = v
                    self._write_json(self.appointments_file, appointments)
                    return dict(appt)
            return None

    # ==========================
    # BLOCKED SCHEDULES
    # ==========================
    def get_blocked_schedules(self) -> Dict[str, List]:
        return self._read_json(self.blocked_schedules_file, {"blocked_days": [], "blocked_times": []})

    def get_blocked_days(self, date_val: Optional[Union[str, date]] = None) -> List[Dict[str, Any]]:
        data = self.get_blocked_schedules()
        days = data.get("blocked_days", [])
        if date_val:
            d_str = str(date_val)
            return [d for d in days if str(d.get("date")) == d_str]
        return days

    def get_blocked_times(self, date_val: Optional[Union[str, date]] = None) -> List[Dict[str, Any]]:
        data = self.get_blocked_schedules()
        times = data.get("blocked_times", [])
        if date_val:
            d_str = str(date_val)
            return [t for t in times if str(t.get("date")) == d_str]
        return times

    # ==========================
    # CLINIC & AGENT CONFIG
    # ==========================
    def get_clinic_config(self) -> Dict[str, Any]:
        return self._read_json(self.clinic_config_file, {
            "clinic_name": "Petfy Clínica & Petshop",
            "address": "Av. Paulista, 1000 - São Paulo, SP",
            "latitude": -23.561684,
            "longitude": -46.655981,
            "timezone": "America/Sao_Paulo",
            "working_hours": {
                "monday": {"start": "08:00", "end": "18:00"},
                "tuesday": {"start": "08:00", "end": "18:00"},
                "wednesday": {"start": "08:00", "end": "18:00"},
                "thursday": {"start": "08:00", "end": "18:00"},
                "friday": {"start": "08:00", "end": "18:00"},
                "saturday": {"start": "08:00", "end": "14:00"},
                "sunday": None
            }
        })

    def update_clinic_config(self, **kwargs) -> Dict[str, Any]:
        with self._lock:
            config = self.get_clinic_config()
            for k, v in kwargs.items():
                if v is not None:
                    config[k] = v
            self._write_json(self.clinic_config_file, config)
            return config

    def get_agent_config(self) -> Dict[str, Any]:
        return self._read_json(self.agent_config_file, {
            "agent_name": "Júlia",
            "is_active": True,
            "tone": "friendly",
            "language": "pt-BR",
            "formality": "informal",
            "emoji_use": "moderate",
            "audio_use": "none",
            "voice_style": "warm",
            "voice": "alloy",
            "process_audio": False,
            "response_delay": 0,
            "evolution_info": None
        })

    def update_agent_config(self, **kwargs) -> Dict[str, Any]:
        with self._lock:
            config = self.get_agent_config()
            for k, v in kwargs.items():
                if v is not None:
                    config[k] = v
            self._write_json(self.agent_config_file, config)
            return config

    # ==========================
    # CONVERSATIONS / STATES
    # ==========================
    def get_agent_state(self, clean_number: str) -> Optional[Dict[str, Any]]:
        conversations = self._read_json(self.conversations_file, {})
        return conversations.get(str(clean_number))

    def save_agent_state(self, clean_number: str, state_data: Dict[str, Any], client_id: Optional[int] = None):
        with self._lock:
            conversations = self._read_json(self.conversations_file, {})
            key = str(clean_number)
            if client_id is not None:
                state_data["client_id"] = client_id
            conversations[key] = state_data
            self._write_json(self.conversations_file, conversations)

    # ==========================
    # PRODUCTS
    # ==========================
    def search_products(self, product_name: str) -> List[Dict[str, Any]]:
        products = self._read_json(self.products_file, [])
        target = product_name.lower().strip()
        return [p for p in products if target in str(p.get("name", "")).lower()]

# Singleton accessor
db = LocalDB()
