from datetime import datetime, timedelta, time
from typing import List, Union, Optional
from database.services import (
    BlockedScheduleService,
    ClinicConfigService,
    appointment_service,
    ServiceService,
    PetService
)
from database.local_db import db


def check_availability(service_id: Union[int, List[int]], date: str, hour: str, org_id: int = 1, exclude_appointment_id: Optional[int] = None):
    """
    Checks availability and returns next available slot for the SAME DAY.
    """
    service_ids = [service_id] if isinstance(service_id, int) else service_id

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(hour, "%H:%M").time()
        start_time = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        return {
            "available": False,
            "next_available_same_day": None,
            "message": f"Data ou horário inválido: {str(e)}"
        }

    total_duration = 0
    services_found = []

    for sid in service_ids:
        service = ServiceService.get_service_by_id(service_id=sid, org_id=org_id)
        if not service:
            return {
                "available": False,
                "next_available_same_day": None,
                "message": f"Serviço ID {sid} não encontrado"
            }
        total_duration += service.get("duration_minutes", 30)
        services_found.append(service)

    duration = total_duration
    end_time = start_time + timedelta(minutes=duration)

    # 1. Verifica se o dia está bloqueado
    blocked_days = BlockedScheduleService.get_blocked_days(org_id, date_obj)
    if blocked_days:
        return {
            "available": False,
            "next_available_same_day": None,
            "message": "Clínica fechada neste dia"
        }

    # 2. Verifica se é dia de funcionamento
    clinic_config = ClinicConfigService.get_clinic_config(org_id)
    working_hours = clinic_config.get('working_hours', {})

    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_name = day_names[date_obj.weekday()]

    if not working_hours.get(day_name) or working_hours[day_name] is None:
        return {
            "available": False,
            "next_available_same_day": None,
            "message": "Clínica fechada neste dia da semana"
        }

    # 3. Verifica se o horário está dentro do expediente
    wh = working_hours[day_name]
    start_work = datetime.strptime(wh['start'], "%H:%M").time()
    end_work = datetime.strptime(wh['end'], "%H:%M").time()

    if time_obj < start_work or time_obj >= end_work:
        return {
            "available": False,
            "next_available_same_day": None,
            "message": f"Fora do horário de funcionamento ({wh['start']} - {wh['end']})"
        }

    work_end_dt = datetime.combine(date_obj, end_work)
    if end_time > work_end_dt:
        return {
            "available": False,
            "next_available_same_day": None,
            "message": "O atendimento ultrapassa o horário de funcionamento"
        }

    # 4. Busca bloqueios e agendamentos
    blocked_times = BlockedScheduleService.get_blocked_times(org_id, date_obj)
    appointments_result = appointment_service.get_appointments_by_org(org_id=org_id, page_size=1000)
    all_appointments = appointments_result.get("appointments", [])

    day_appointments = [
        a for a in all_appointments
        if str(a.get("appointment_date")) == date 
        and a.get("status") == "SCHEDULED"
        and (exclude_appointment_id is None or a.get("id") != exclude_appointment_id)
    ]

    # 5. Cria lista de períodos ocupados
    occupied_periods = []

    for bt in blocked_times:
        bt_start = bt['start_time'] if isinstance(bt['start_time'], time) else datetime.strptime(bt['start_time'], "%H:%M").time()
        bt_end = bt['end_time'] if isinstance(bt['end_time'], time) else datetime.strptime(bt['end_time'], "%H:%M").time()
        occupied_periods.append({
            'start': datetime.combine(date_obj, bt_start),
            'end': datetime.combine(date_obj, bt_end),
            'type': 'blocked'
        })

    for appt in day_appointments:
        appt_time_val = appt["appointment_time"]
        if isinstance(appt_time_val, str):
            appt_time = datetime.strptime(appt_time_val, "%H:%M").time()
        else:
            appt_time = appt_time_val
        appt_duration = appt.get("duration_minutes", 30)
        appt_start_dt = datetime.combine(date_obj, appt_time)
        appt_end_dt = appt_start_dt + timedelta(minutes=appt_duration)
        occupied_periods.append({
            'start': appt_start_dt,
            'end': appt_end_dt,
            'type': 'appointment'
        })

    occupied_periods.sort(key=lambda x: x['start'])

    # 6. Verifica conflitos
    for period in occupied_periods:
        if start_time < period['end'] and end_time > period['start']:
            next_available = find_next_available_slot(
                period['end'],
                work_end_dt,
                duration,
                occupied_periods
            )
            message = "Horário bloqueado" if period['type'] == 'blocked' else "Horário já ocupado"
            return {
                "available": False,
                "next_available_same_day": next_available,
                "message": message
            }

    return {
        "available": True,
        "next_available_same_day": hour,
        "total_duration": duration,
        "services_count": len(services_found)
    }


def find_next_available_slot(start_search_time, work_end_dt, duration, occupied_periods):
    current_time = start_search_time
    duration_delta = timedelta(minutes=duration)
    increment = timedelta(minutes=30)

    while current_time + duration_delta <= work_end_dt:
        slot_end = current_time + duration_delta
        is_available = True
        for period in occupied_periods:
            if current_time < period['end'] and slot_end > period['start']:
                current_time = period['end']
                is_available = False
                break

        if is_available:
            return current_time.strftime("%H:%M")

        if not is_available:
            continue

        current_time += increment

    return None


def create_schedule(client_id: int, service_id: Union[int, List[int]], pet_id: int, date: str, hour: str, org_id: int = 1):
    availability = check_availability(service_id, date, hour, org_id)
    if not availability["available"]:
        next_time = availability.get("next_available_same_day")
        if next_time:
            message = f"Time slot unavailable. The next available time today is {next_time}."
        else:
            message = "Time slot unavailable. There are no more available times today."
        return {"success": False, "message": message}

    service_ids = [service_id] if isinstance(service_id, int) else service_id
    total_duration = 0
    for sid in service_ids:
        service = ServiceService.get_service_by_id(service_id=sid, org_id=org_id)
        if service:
            total_duration += service.get("duration_minutes", 30)

    appt = db.create_appointment(
        client_id=client_id,
        pet_id=pet_id,
        service_id=service_ids,
        appointment_date=date,
        appointment_time=hour,
        duration_minutes=total_duration
    )
    return {"success": True, "message": "Appointment successfully scheduled.", "data": appt}


def get_past_schedules_list(client_id: int, org_id: int = 1):
    appts = [a for a in db.get_appointments() if a.get("client_id") == client_id]
    return [
        {
            "id": appt["id"],
            "client_id": appt["client_id"],
            "service": ServiceService.get_service_by_id(service_id=appt.get("service_id", 1), org_id=org_id),
            "pet": PetService.get_pet_by_id(appt.get("pet_id", 1), org_id=org_id),
            "date": appt.get("appointment_date"),
            "hour": appt.get("appointment_time"),
            "status": appt.get("status")
        } for appt in appts
    ]


def cancel_schedule(schedule_id: int, org_id: int = 1):
    return db.update_appointment(schedule_id, status="CANCELLED")


def edit_schedule(schedule_id: int, date: str = None, hour: str = None, pet_id: int = None, service_id: Union[int, List[int]] = None, org_id: int = 1):
    kwargs = {}
    if date:
        kwargs["appointment_date"] = date
    if hour:
        kwargs["appointment_time"] = hour
    if pet_id:
        kwargs["pet_id"] = pet_id
    if service_id:
        service_ids = [service_id] if isinstance(service_id, int) else service_id
        kwargs["service_id"] = service_ids[0]
        kwargs["service_ids"] = service_ids

    return db.update_appointment(schedule_id, **kwargs)
