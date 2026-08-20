import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.route("/", methods=["GET"])
def home():
    return "TeZgo Taxi Bot is running!"


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        if message["type"] == "text":
            user_phone = message["from"]
            text = message["text"]["body"].strip().lower()

            if text in ["такси", "taxi", "привет", "здравствуйте", "здравствуй"]:
                reply = (
                    "🚕 Добро пожаловать в TeZgo Taxi!\n\n"
                    "Чтобы заказать такси, напишите:\n"
                    "📍 Откуда вас забрать?\n"
                    "📍 Куда едем?"
                )
            else:
                reply = (
                    "🚕 TeZgo Taxi\n\n"
                    "Чтобы заказать такси, напишите «Такси»."
                )

            send_message(user_phone, reply)

    except Exception as e:
        print("Webhook error:", e)

    return "OK", 200


def send_message(to, text):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    requests.post(url, headers=headers, json=data, timeout=20)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
