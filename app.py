import os
import json
import requests

from fastapi import FastAPI, Request, HTTPException

# ==================================================
# Environment Variables
# ==================================================

LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

if not LINE_TOKEN:
    raise ValueError("LINE_TOKEN not found")

if not LINE_SECRET:
    raise ValueError("LINE_SECRET not found")

# ==================================================
# LINE API
# ==================================================

LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"

# ==================================================
# FastAPI
# ==================================================

app = FastAPI()


@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "20260810"
    }


@app.post("/webhook")
async def handle_webhook(request: Request):

    payload = await request.json()

    print("========== WEBHOOK ==========")
    print(json.dumps(payload, ensure_ascii=False))

    events = payload.get("events", [])

    if not events:
        return {"status": "no event"}

    event = events[0]

    if event.get("type") != "message":
        return {"status": "ignore"}

    if event["message"].get("type") != "text":
        return {"status": "ignore"}

    reply_token = event["replyToken"]
    user_text = event["message"]["text"]

    reply_text = f"你剛剛說了：{user_text}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": reply_text
            }
        ]
    }

    response = requests.post(
        LINE_REPLY_ENDPOINT,
        headers=headers,
        json=data
    )

    print("LINE Response:", response.status_code)
    print(response.text)

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
