import os
import json
import requests
import uvicorn

from fastapi import FastAPI, Request

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

line_reply_endpoint="https://api.line.me/v2/bot/message/reply"

# ==================================================
# FastAPI
# ==================================================

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status":"ok",
    }

@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    event = payload["events"][0] # 擷取payload 內的replyToken 和訊息
    reply_token = event["replyToken"]
    message = event["message"]["text"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "replyToken": reply_token, # 需要有replyToken 才能回覆
        "messages": [
            {
                "type": "text",
                "text": f"重複⼀次：{message}",
            }
        ]
    }
    requests.post(line_reply_endpoint, headers=headers, data=json.dumps(data))

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
