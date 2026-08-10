import os
from fastapi import FastAPI, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)

from linebot.v3.webhooks import MessageEvent, TextMessageContent


# =====================================
# 讀取 Render Environment Variables
# =====================================

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_SECRET")

if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN not found")

if not CHANNEL_SECRET:
    raise ValueError("LINE_CHANNEL_SECRET not found")


# =====================================
# LINE SDK
# =====================================

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(CHANNEL_SECRET)


# =====================================
# FastAPI
# =====================================

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):

    signature = request.headers.get("X-Line-Signature")

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing X-Line-Signature"
        )

    body = await request.body()
    body_str = body.decode("utf-8")

    print("========== WEBHOOK ==========")
    print(body_str)

    try:
        handler.handle(body_str, signature)

    except InvalidSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Signature"
        )

    return {"status": "success"}


# =====================================
# 收到文字訊息
# =====================================

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_text = event.message.text

    reply_text = f"你剛剛說：{user_text}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=reply_text)
                ]
            )
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
