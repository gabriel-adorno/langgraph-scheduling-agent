"""
Modo interativo (CLI) para testar o agente de agendamento localmente.
Suporta:
    • Mensagens de texto normais
    • Gravação de voz real pelo microfone (/gravar ou /mic)
    • Simulação de áudio via texto (/audio <mensagem>)
    • Reprodução de áudio nos alto-falantes APENAS quando o agente responder com áudio
"""
import os
import sys
import time
import base64
import signal
import shutil
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

from dotenv import load_dotenv
load_dotenv()

from agent.graph.process_message import process_message
from agent.utils.functions import get_message_id, text_to_audio_base64
from database.local_db import db


def find_ffmpeg() -> str | None:
    """Localiza o binário do FFmpeg no sistema."""
    for path in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.exists(path):
            return path
    return shutil.which("ffmpeg")


def record_voice_from_microphone() -> str | None:
    """
    Grava áudio diretamente do microfone do Mac usando FFmpeg.
    Retorna o áudio codificado em base64 ou None se cancelado/falhar.
    """
    ffmpeg_bin = find_ffmpeg()
    if not ffmpeg_bin:
        print("\n❌ FFmpeg não encontrado!")
        print("💡 Para gravar pelo microfone, instale o FFmpeg no Mac: brew install ffmpeg\n")
        return None

    # Arquivo temporário WAV
    tmp_fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="petfy_mic_")
    os.close(tmp_fd)

    # Dispositivos de entrada para testar no macOS AVFoundation
    # ':default' usa o microfone padrão do sistema; ':0' é o primeiro dispositivo de áudio
    devices_to_try = [":default", ":0"]
    proc = None

    for dev in devices_to_try:
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loglevel", "error",
            "-f", "avfoundation",
            "-i", dev,
            "-ac", "1",
            "-ar", "16000",
            tmp_wav
        ]
        try:
            import subprocess
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            time.sleep(0.3)
            # Se o processo continua rodando, o dispositivo foi aberto com sucesso
            if proc.poll() is None:
                break
        except Exception:
            proc = None
            continue

    if not proc or proc.poll() is not None:
        print("\n❌ Não foi possível acessar o microfone.")
        print("💡 Dica: Verifique se o seu Terminal tem permissão de Microfone em:")
        print("   Ajustes do Sistema > Privacidade e Segurança > Microfone.\n")
        Path(tmp_wav).unlink(missing_ok=True)
        return None

    print("\n" + "─" * 60)
    print("🎙️  GRAVANDO ÁUDIO... Fale normalmente no seu microfone!")
    print("👉 Pressione [ENTER] para parar a gravação e enviar ao agente...")
    print("─" * 60)

    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

    # Finaliza a gravação com segurança
    try:
        if proc.stdin:
            try:
                proc.stdin.write(b"q\n")
                proc.stdin.flush()
            except Exception:
                pass
        time.sleep(0.3)
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            time.sleep(0.3)
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=2)
    except Exception:
        pass

    # Verifica se o arquivo tem conteúdo válido (mínimo ~1KB)
    if os.path.exists(tmp_wav) and os.path.getsize(tmp_wav) > 1000:
        with open(tmp_wav, "rb") as f:
            audio_bytes = f.read()
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        Path(tmp_wav).unlink(missing_ok=True)
        print("🎧 Gravação concluída com sucesso! Enviando áudio...")
        return audio_b64
    else:
        Path(tmp_wav).unlink(missing_ok=True)
        print("⚠️ Gravação muito curta ou vazia. Tente novamente.")
        return None


def main():
    print("=" * 65)
    print("🐾 Agente de Agendamento — Modo Terminal Interativo")
    print("=" * 65)
    print("Simula uma conversa real de WhatsApp com o agente inteligente.")
    print("\nComandos disponíveis:")
    print("  • Digite qualquer texto  → Envia mensagem de texto normal")
    print("  • /gravar ou /mic        → Grava sua voz no microfone do Mac")
    print("  • /audio <mensagem>      → Simula envio de áudio com esse texto")
    print("  • sair ou exit           → Encerra o chat\n")
    print("🔊 Regra de áudio:")
    print("  • Respostas em TEXTO ficam em silêncio.")
    print("  • Respostas em ÁUDIO tocam automaticamente nos alto-falantes!\n")
    print("-" * 65)

    user_num = 5511999999999

    while True:
        try:
            user_input = input("\nVOCÊ (ou /gravar): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando. Até mais! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("sair", "exit", "quit"):
            print("Encerrando. Até mais! 👋")
            break

        msg_mode = "text"
        actual_content = user_input
        audio_b64 = None

        # 1. Comando de gravação real pelo microfone
        if user_input.lower() in ("/gravar", "/mic", "/rec"):
            audio_b64 = record_voice_from_microphone()
            if not audio_b64:
                continue
            msg_mode = "audio"
            actual_content = None

        # 2. Comando de simulação de áudio via texto
        elif user_input.lower().startswith("/audio "):
            simulated_text = user_input[7:].strip()
            if not simulated_text:
                print("⚠️ Digite o conteúdo após /audio (Ex: /audio Gostaria de marcar banho)")
                continue
            print(f"🎙️ [Simulando envio de áudio: '{simulated_text}']")
            msg_mode = "audio"
            # Sintetiza o áudio para passar pelo pipeline completo (Whisper -> Transcrição)
            try:
                audio_b64 = text_to_audio_base64(simulated_text, voice="alloy")
            except Exception:
                audio_b64 = None
            actual_content = simulated_text if not audio_b64 else None

        user_msg = {
            "id": get_message_id(),
            "org_id": 1,
            "user_num": user_num,
            "mode": msg_mode,
            "base64": audio_b64,
            "reply_to": None,
            "content": actual_content,
            "caption": None,
            "is_from_me": False,
            "push_name": None
        }

        # Processa mensagem de forma síncrona
        # O agente tocará o áudio automaticamente nos alto-falantes via whatsapp_functions
        # SOMENTE se a resposta gerada for mode == 'audio'.
        process_message(user_msg, synchronous=True)


if __name__ == "__main__":
    main()
