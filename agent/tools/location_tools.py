from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from database.services import ClinicConfigService
from agent.db.whatsapp_functions import send_location_message, send_message

@tool
def send_location_tool(
        org_id: Annotated[int, InjectedState("org_id")],
        client_info: Annotated[dict, InjectedState("client_info")],
        agent_config: Annotated[dict, InjectedState("agent_config")]) -> dict:
    """
    Envia a localização da clínica para o cliente via WhatsApp.
    Se houver latitude e longitude configuradas, envia um pin de localização.
    Caso contrário, se houver endereço, envia como texto formatado.
    """
    user_num = client_info.get("number")
    if not user_num:
        return {"success": False, "message": "Número de telefone do cliente não encontrado."}

    evolution_info = agent_config.get("technical_settings", {}).get("evolution_info") if agent_config else None
    clinic_config = ClinicConfigService.get_clinic_config(org_id)

    clinic_name = clinic_config.get("clinic_name", "Nossa Clínica")
    address = clinic_config.get("address")
    latitude = clinic_config.get("latitude")
    longitude = clinic_config.get("longitude")

    if latitude is not None and longitude is not None:
        success = send_location_message(
            latitude=float(latitude),
            longitude=float(longitude),
            evolution_info=evolution_info,
            number=user_num,
            name=clinic_name,
            address=address
        )
        if success:
            return {
                "success": True,
                "message": "Localização enviada com sucesso! O cliente recebeu o pin de localização."
            }
        else:
            return {"success": False, "message": "Erro ao enviar localização."}

    elif address:
        message_text = f"📍 *Nossa localização:*\n\n{address}"
        message_obj = {"mode": "text", "content": message_text, "reply_to": None}
        message_id = send_message(org_id, message_obj, evolution_info, user_num)
        if message_id:
            return {
                "success": True,
                "message": "Endereço enviado com sucesso!"
            }
        else:
            return {"success": False, "message": "Erro ao enviar endereço."}

    return {
        "success": False,
        "message": "A localização da clínica não está configurada."
    }

location_tools = [send_location_tool]
