import os
import uuid
import requests
from agent.utils.functions import text_to_audio_base64, calculate_delay, play_audio_locally
from agent.db.state_functions import get_agent_config

def send_location_message(latitude: float, longitude: float, evolution_info: dict = None, number: str = "", name: str = None, address: str = None) -> bool:
    """Envia localização via Evolution API ou simula localmente."""
    print(f"\n📍 [LOCALIZAÇÃO] Para: {number} | Lat: {latitude}, Lng: {longitude} | Nome: {name} | Endereço: {address}")

    if not evolution_info or not evolution_info.get("server_url"):
        print("ℹ️ Evolution API não configurada. Localização registrada localmente.")
        return True

    try:
        url = f"{evolution_info['server_url']}/message/sendLocation/{evolution_info['instance']}"
        payload = {
            "number": f"{number}@s.whatsapp.net",
            "latitude": latitude,
            "longitude": longitude
        }
        if name:
            payload["name"] = name
        if address:
            payload["address"] = address

        headers = {
            "apikey": evolution_info.get("api_key") or os.getenv("EVOLUTION_API_GLOBAL_KEY", ""),
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"⚠️ Erro ao enviar localização via Evolution API: {e}")
        return True


def send_message(org_id: int, message: dict, evolution_info: dict = None, number: str = "") -> str:
    """
    Envia mensagem usando Evolution API (se configurada) ou simula localmente.
    Retorna o ID da mensagem.
    """
    local_id = f"local_msg_{uuid.uuid4().hex[:8]}"
    content = message.get("content", "")
    mode = message.get("mode", "text")

    print(f"\n🤖 [RESPOSTA DO AGENTE] ({mode.upper()}) para {number}:")
    print(f"   {content}\n")

    audio_b64 = None
    if mode == "audio":
        agent_config = get_agent_config(org_id)
        personality = agent_config.get("personality", {}) if agent_config else {}
        voice = personality.get("voice", "alloy")
        voice_style = personality.get("voice_style", "neutral")
        audio_b64 = text_to_audio_base64(content, voice, voice_style)
        # Reproduz o áudio nos alto-falantes do computador
        play_audio_locally(audio_b64=audio_b64, text=content)

    if not evolution_info or not evolution_info.get("server_url"):
        return local_id

    try:
        agent_config = get_agent_config(org_id)
        personality = agent_config.get("personality", {}) if agent_config else {}
        voice = personality.get("voice", "alloy")
        voice_style = personality.get("voice_style", "neutral")

        headers = {
            "apikey": evolution_info.get("api_key") or os.getenv("EVOLUTION_API_GLOBAL_KEY", ""),
            "Content-Type": "application/json"
        }

        if mode == "text":
            url = f"{evolution_info['server_url']}/message/sendText/{evolution_info['instance']}"
            payload = {
                "number": f"{number}@s.whatsapp.net",
                "text": content,
                "delay": 0,
                "linkPreview": True
            }
        elif mode == "audio":
            url = f"{evolution_info['server_url']}/message/sendWhatsAppAudio/{evolution_info['instance']}"
            if not audio_b64:
                audio_b64 = text_to_audio_base64(content, voice, voice_style)
            payload = {
                "number": f"{number}@s.whatsapp.net",
                "audio": audio_b64,
                "delay": calculate_delay(content, mode),
                "linkPreview": True
            }
        else:
            return local_id

        if message.get("reply_to"):
            payload["quoted"] = {
                "key": {
                    "id": message["reply_to"],
                    "fromMe": False,
                    "remoteJid": f"{number}@s.whatsapp.net"
                },
                "message": {
                    "conversation": "mensagem original"
                }
            }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            data = response.json()
            return data.get("key", {}).get("id", local_id)
        else:
            print(f"⚠️ Evolution API respondeu com status {response.status_code}: {response.text}")
            return local_id
    except Exception as e:
        print(f"⚠️ Erro ao conectar com Evolution API: {e}")
        return local_id
