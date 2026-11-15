from agent.states.all_states import AgentState

def update_step(state: AgentState) -> AgentState:
    client_info = state.get("client_info", {})
    schedule_info = state.get("schedule_info", {})

    # 🧭 Modo de gerenciamento de agendamentos
    if state.get("is_in_schedule_management"):
        state["step"] = "MANAGE_SCHEDULE"
        return state

    # 1️⃣ Nenhum cliente ainda — precisa registrar
    if not client_info.get("id"):
        state["step"] = "REGISTER_CLIENT"
        return state

    # 2️⃣ Cliente já registrado, mas ainda não escolheu o serviço
    if not schedule_info.get("service_id"):
        state["step"] = "CHOOSE_SERVICE"
        return state

    # 3️⃣ Serviço escolhido, mas ainda não selecionou o pet
    if not schedule_info.get("pet_id"):
        state["step"] = "CHOOSE_PET"
        return state

    # 4️⃣ Pet escolhido, mas ainda falta data/hora
    if not schedule_info.get("date") or not schedule_info.get("hour"):
        state["step"] = "CHOOSE_DATE"
        return state

    # 5️⃣ Tudo preenchido — pronto para confirmar o agendamento
    state["step"] = "CONFIRM_SCHEDULE"
    return state
