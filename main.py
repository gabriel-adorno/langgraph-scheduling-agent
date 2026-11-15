import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import json
from fastapi import FastAPI, Request
import uvicorn

from agent.graph.process_message import process_message
from agent.utils.functions import get_message_id

app = FastAPI()

@app.post("/receive-message")
async def receive_message(request: Request):
    event = await request.json()
    print(json.dumps(event, indent=4, ensure_ascii=False))

    data = event.get("data", {})
    key = data.get("key", {})
    message = data.get("message", {})

    mode = "text"
    content = None
    base64_data = None
    caption = None

    if "conversation" in message:
        mode = "text"
        content = message["conversation"]
    elif "audioMessage" in message:
        mode = "audio"
        base64_data = message.get("base64")
    elif "imageMessage" in message:
        mode = "image"
        base64_data = message.get("base64")
        caption = message.get("imageMessage", {}).get("caption", None)
    else:
        mode = "text"
        content = str(message)

    reply_to = None
    context_info = message.get("contextInfo") or data.get("contextInfo", {})
    if context_info:
        reply_to = context_info.get("stanzaId", None)

    push_name = None
    is_from_me = key.get("fromMe", False)
    if not is_from_me:
        push_name = data.get("pushName", None)

    user_msg = {
        "id": key.get("id") or get_message_id(),
        "org_id": 1,
        "user_num": int(key.get("remoteJid", "0").split("@")[0]),
        "mode": mode,
        "base64": base64_data,
        "reply_to": reply_to,
        "content": content,
        "caption": caption,
        "is_from_me": is_from_me,
        "push_name": push_name
    }

    print(json.dumps(user_msg, indent=4, ensure_ascii=False))
    process_message(user_msg)

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
