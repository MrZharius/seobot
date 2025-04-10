# webhook.py
from flask import Flask, request, jsonify
from db import set_premium
import hmac
import hashlib
import json

app = Flask(__name__)

# Для простоты webhook открыт (можно добавить секретную проверку сигнатур)

@app.route("/yookassa-webhook", methods=["POST"])
def yookassa_webhook():
    event = request.json
    if not event:
        return jsonify({"error": "no data"}), 400

    # Проверяем, что оплата успешна
    if event.get("event") == "payment.succeeded":
        metadata = event["object"]["metadata"]
        user_id = int(metadata.get("user_id"))
        set_premium(user_id)
        return jsonify({"status": "ok"}), 200

    return jsonify({"status": "ignored"}), 200

if __name__ == "__main__":
    app.run(port=8000)
