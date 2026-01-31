import requests

ACCESS_TOKEN = "EAARwDBOSWfkBQhZAZCu70ZAq4a9IZCaTXEl5cVPJFuWB96RVL3g0gCWQ4ZALnR7OZBGzBH1kQiql3zascVY76jSgJ0RTzEwIr3Kl78l8NmZBZBsoquBYEPT3bwYH9VqC1LYKoD3XZBHOFe5xIM0iPptpC71ZCe9jXthNcTo47wKEcNJPPv6ydPBqQSFdcOVHZCzGDJk9qedAnXBAuAYjMh95ml3kKzccBAA3hyCz71KgCUZCeexgCQJ6MlIYa5rGgbxzN6Jsvv5bLZAGvzZBjJ6RqwgekZCdEmn"
PHONE_NUMBER_ID = "928126690390752"
TO_PHONE = "918220252861"

url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

payload = {
    "messaging_product": "whatsapp",
    "to": TO_PHONE,
    "type": "text",
    "text": {
        "body": "Hello! 👋\nThank you for contacting us. How can we help you today?"
    }
}

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.text)
