import json
import locale
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain_core.messages import SystemMessage, HumanMessage
from agent.states.all_states import AgentState, AgentAction
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import base64
import tempfile
from pathlib import Path
from openai import OpenAI
import os

load_dotenv()

audio_llm = None
llm = None
openai_client = None

def has_repeated_user_messages(messages: list, threshold: int = 3) -> bool:
    """Verifica se as últimas N mensagens do usuário são idênticas (spam)."""
    user_messages = []
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            try:
                parsed = json.loads(msg.content)
                content = parsed.get("content", "")
            except (json.JSONDecodeError, TypeError):
                content = msg.content
            
            user_messages.append(content)
            if len(user_messages) >= threshold:
                break
    
    if len(user_messages) < threshold:
        return False
    
    return len(set(user_messages[:threshold])) == 1


def get_llm_model() -> str:
    return os.getenv("LLM_MODEL", "gpt-4o-mini")


def get_llm(api_key: str = None):
    global llm
    effective_key = api_key or os.getenv("OPENAI_API_KEY")
    if llm is None or api_key:
        llm = ChatOpenAI(model=get_llm_model(), api_key=effective_key)
    return llm


_msg_id_counter = 0

def get_message_id():
    global _msg_id_counter
    _msg_id_counter += 1
    return str(_msg_id_counter)


def should_use_tool(state: AgentState) -> str:
    if not state.get("messages"):
        return "end_edge"
    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", None)
    if tool_calls:
        return "tool_edge"
    return "end_edge"


def safe_load_json(content):
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return content


def get_local_datetime_text(timezone: str = "America/Sao_Paulo"):
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "pt_BR")
        except locale.Error:
            locale.setlocale(locale.LC_TIME, "C")

    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:
        now = datetime.now()

    return now.strftime("%A, %d de %B de %Y às %Hh%M")


def parse_agent_action(content: str, api_key: str = None) -> AgentAction:
    system_msg = SystemMessage(content=(
        "You must strictly output a valid JSON that matches the AgentAction schema: "
        "{ mode: 'text' | 'audio', reply_to: string | null, content: string }. "
        "Do not include explanations. Only return the JSON."))

    result = get_llm(api_key).invoke(
        [system_msg, HumanMessage(content=content)],
        response_format=AgentAction)
    return result


def get_openai_client(api_key: str = None):
    global openai_client
    effective_key = api_key or os.getenv("OPENAI_API_KEY")
    if openai_client is None or api_key:
        openai_client = OpenAI(api_key=effective_key)
    return openai_client


def transcribe_audio(msg_base64: str, api_key: str = None) -> str:
    """Transcreve áudio base64 usando OpenAI Whisper."""
    if not msg_base64:
        return "[error_no_audio_base64]"

    try:
        audio_bytes = base64.b64decode(msg_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        try:
            with open(tmp_file_path, "rb") as f:
                response = get_openai_client(api_key).audio.transcriptions.create(
                    file=f, model="whisper-1")
            return response.text
        finally:
            Path(tmp_file_path).unlink(missing_ok=True)
    except Exception as e:
        return f"[error_transcribing_audio: {e}]"


def text_to_audio_base64(text: str,
                         voice: str = "alloy",
                         voice_style: str = "neutral",
                         api_key: str = None):
    """Converte texto em áudio usando OpenAI TTS (tts-1 ou gpt-4o-mini-tts) e retorna base64."""
    style_instructions = {
        "warm": "Keep the natural default voice, adding only a light touch of warmth and calm friendliness, without changing rhythm or style.",
        "neutral": None,
        "enthusiastic": "Maintain the default voice style while adding a gentle hint of positive energy, without becoming overly expressive or dramatic."
    }

    instruction = style_instructions.get(voice_style, None)
    
    # Tenta com gpt-4o-mini-tts se houver instrução, ou tts-1 padrão
    payload = {
        "model": "gpt-4o-mini-tts" if instruction else "tts-1",
        "voice": voice,
        "input": text,
    }
    if instruction is not None:
        payload["instructions"] = instruction

    try:
        response = get_openai_client(api_key).audio.speech.create(**payload)
        audio_bytes = response.read()
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        # Fallback para modelo tts-1 padrão da OpenAI
        try:
            payload_fallback = {"model": "tts-1", "voice": voice, "input": text}
            response = get_openai_client(api_key).audio.speech.create(**payload_fallback)
            audio_bytes = response.read()
            return base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e2:
            print(f"⚠️ Erro ao gerar áudio com OpenAI: {e2}")
            return None


def play_audio_locally(audio_b64: str = None, text: str = None):
    """
    Toca o áudio diretamente nos alto-falantes do computador (macOS / Linux / Windows).
    - Se houver audio_b64 da OpenAI: decodifica e toca usando 'afplay' (macOS) nativo.
    - Se falhar ou estiver offline: faz fallback automático usando comando 'say' do Mac.
    """
    import subprocess
    import shutil

    # 1. Toca o arquivo de áudio gerado pelo OpenAI TTS
    if audio_b64:
        try:
            audio_bytes = base64.b64decode(audio_b64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name

            if shutil.which("afplay"):
                print("🔊 [Tocando áudio da OpenAI nos alto-falantes...]")
                subprocess.run(["afplay", tmp_path], check=False)
                Path(tmp_path).unlink(missing_ok=True)
                return True
        except Exception as e:
            print(f"⚠️ Erro ao tocar via afplay: {e}")

    # 2. Fallback offline: sintetizador de voz nativo do macOS ('say')
    if text and shutil.which("say"):
        try:
            print("🔊 [Reproduzindo via sintetizador de voz do macOS...]")
            subprocess.run(["say", text], check=False)
            return True
        except Exception as e:
            print(f"⚠️ Erro no comando say: {e}")

    return False


def calculate_delay(content: str, mode: str = "text") -> int:
    if mode == "text":
        return max(500, len(content) * 60)
    elif mode == "audio":
        return max(1000, len(content) * 50)
    return 0
