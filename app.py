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

        if message.get("type") != "text":
            return "OK", 200

        from_number = message["from"]
        text = message["text"]["body"].strip()

        reply = (
            "🚕 Добро пожаловать в TeZgo Taxi!\n\n"
            "Чтобы заказать такси, напишите адрес, откуда вас забрать.\n\n"
            "Например:\n"
            "Айдаркен, центр\n\n"
            "После этого мы продолжим оформление заказа."
        )

        send_message(from_number, reply)

    except Exception as e:
        print("Webhook error:", e)

    return "OK", 200


def send_message(to, text):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )

    print("WhatsApp response:", response.status_code, response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
