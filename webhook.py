from flask import Flask, request
import requests

app = Flask(__name__)

# 🔑 WhatsApp Cloud API details
ACCESS_TOKEN = "EAARwDBOSWfkBQhZAZCu70ZAq4a9IZCaTXEl5cVPJFuWB96RVL3g0gCWQ4ZALnR7OZBGzBH1kQiql3zascVY76jSgJ0RTzEwIr3Kl78l8NmZBZBsoquBYEPT3bwYH9VqC1LYKoD3XZBHOFe5xIM0iPptpC71ZCe9jXthNcTo47wKEcNJPPv6ydPBqQSFdcOVHZCzGDJk9qedAnXBAuAYjMh95ml3kKzccBAA3hyCz71KgCUZCeexgCQJ6MlIYa5rGgbxzN6Jsvv5bLZAGvzZBjJ6RqwgekZCdEmn"
PHONE_NUMBER_ID = "928126690390752"

# 📤 Send message function
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

# 🔔 Webhook verification (IMPORTANT)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = "my_verify_token"

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    return "Verification failed", 403

# 📩 Receive messages
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user_text = message["text"]["body"].lower()
        from_number = message["from"]

        # 🧠 Bot logic
        if "hi" in user_text:
            reply = "Hi 👋 Vanakkam! Sollunga, enna help venum? 😊"
        elif "help" in user_text:
            reply = "Sure 👍 Ungal query-ai clear-ah sollunga."
        else:
            reply = "Nandri 🙏 Naan unga help-ku irukken."

        send_whatsapp_message(from_number, reply)

    except:
        pass

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(port=5000)
