import json
import threading
from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage

from agent.db.state_functions import load_state, save_state, get_agent_config
from agent.states.all_states import DBMessage
from .graph import app
from agent.utils.functions import transcribe_audio, has_repeated_user_messages

message_buffers = defaultdict(list)
timers = {}
lock = threading.Lock()


def invoke_buffered_thread(org_id, user_num, push_name):
    """Função que roda em uma thread para não bloquear input"""
    key = (org_id, user_num)
    with lock:
        agent_config = get_agent_config(org_id)
        if not agent_config:
            return

        history = load_state(org_id,
                             user_num,
                             agent_config,
                             name_suggestion=push_name)
        history["messages"].extend(message_buffers[key])
        message_buffers[key] = []

    result = app.invoke(history)
    save_state(result)

    with lock:
        timers.pop(key, None)
    return result


def process_message(user_msg, synchronous: bool = False):
    msg_id = user_msg.get("id")
    org_id = user_msg.get("org_id", 1)
    user_num = user_msg.get("user_num")
    msg_mode = user_msg.get("mode", "text")
    msg_base64 = user_msg.get("base64")
    msg_content = user_msg.get("content")
    image_caption = user_msg.get("caption")
    is_from_me = user_msg.get("is_from_me", False)
    reply_to = user_msg.get("reply_to")
    push_name = user_msg.get("push_name", None)

    llm_type = "agent" if is_from_me else "user"

    if not user_num:
        print("🚨 Número de usuário não encontrado. Ignorando mensagem.")
        return None

    if len(str(user_num)) > 15:
        print("🚨 Número de usuário inválido. Ignorando mensagem.")
        return None

    agent_config = get_agent_config(org_id)
    ai_enabled = agent_config.get("ai_enabled", True) if agent_config else True
    technical_settings = agent_config.get("technical_settings", {}) if agent_config else {}
    process_audio = technical_settings.get("process_audio", False)
    response_delay = technical_settings.get("response_delay", 0)

    history = load_state(
        org_id, user_num, agent_config,
        name_suggestion=push_name) if agent_config else {"messages": []}

    # Verificar duplicação
    for m in history["messages"]:
        if not hasattr(m, "content") or m.content is None:
            continue
        if not isinstance(m.content, str):
            continue
        try:
            parsed = json.loads(m.content)
        except Exception:
            continue
        if isinstance(parsed, dict) and parsed.get("id") == msg_id:
            print(f"🔄 Mensagem {msg_id} já está no histórico. Ignorando.")
            return None

    # CASO 1 — NÃO ACIONAR IA (is_from_me OU IA DESLIGADA)
    if is_from_me or not ai_enabled:
        print("IA NÃO acionada. Apenas salvando histórico.")
        if msg_mode == "audio":
            if msg_base64:
                msg_content = transcribe_audio(msg_base64) if (ai_enabled and process_audio) else "[audio_not_processed]"
            elif not msg_content:
                msg_content = "[audio_not_processed]"
        elif msg_mode == "image":
            msg_content = "[image_not_processed]"

        db_message = DBMessage(id=msg_id,
                               mode=msg_mode,
                               reply_to=reply_to,
                               content=msg_content)

        if is_from_me:
            user_llm_message = AIMessage(
                content=json.dumps(db_message.model_dump()),
                additional_kwargs={"message_type": llm_type})
        else:
            user_llm_message = HumanMessage(
                content=json.dumps(db_message.model_dump()),
                additional_kwargs={"message_type": llm_type})

        if agent_config:
            history["messages"].append(user_llm_message)
            save_state(history)
        return None

    # CASO 2 — ACIONAR IA NORMALMENTE
    if msg_mode == "audio":
        if msg_base64:
            msg_content = transcribe_audio(msg_base64) if process_audio else "[audio_not_processed]"
        elif not msg_content:
            msg_content = "[audio_not_processed]"
    elif msg_mode == "image":
        msg_content = "[image_not_processed]"

    db_message = DBMessage(id=msg_id,
                           mode=msg_mode,
                           reply_to=reply_to,
                           content=msg_content)

    user_llm_message = HumanMessage(
        content=json.dumps(db_message.model_dump()),
        additional_kwargs={"message_type": llm_type})

    key = (org_id, user_num)

    with lock:
        for m in message_buffers[key]:
            if m.content == user_llm_message.content:
                print(f"🔁 Mensagem {msg_id} já estava no buffer. Ignorando.")
                return None

        message_buffers[key].append(user_llm_message)

        if agent_config:
            history["messages"].append(user_llm_message)
            save_state(history)

        if has_repeated_user_messages(history["messages"], threshold=3):
            print(f"🚫 Spam detectado para {user_num}: últimas 3 mensagens são iguais. Não acionando IA.")
            return None

    if synchronous or response_delay <= 0:
        return invoke_buffered_thread(org_id, user_num, push_name)

    with lock:
        if key not in timers:
            timer = threading.Timer(
                response_delay, lambda: threading.Thread(
                    target=invoke_buffered_thread,
                    args=(org_id, user_num, push_name)).start())
            timers[key] = timer
            timer.start()

    return None
