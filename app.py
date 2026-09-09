import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
LARAVEL_WEBHOOK_URL = os.environ.get("LARAVEL_WEBHOOK_URL", "")
LARAVEL_WEBHOOK_SECRET = os.environ.get("LARAVEL_WEBHOOK_SECRET", "")


@app.route("/")
def home():
    return "Wonder Godoro WhatsApp Webhook is running!"


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    body = request.get_data()

    if not LARAVEL_WEBHOOK_URL or not LARAVEL_WEBHOOK_SECRET:
        return jsonify({"status": "forwarding_failed"}), 500

    forwarded_request = Request(
        LARAVEL_WEBHOOK_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LARAVEL_WEBHOOK_SECRET}",
        },
        method="POST",
    )

    try:
        with urlopen(forwarded_request, timeout=15) as response:
            if 200 <= response.status < 300:
                return jsonify({"status": "received"}), 200

    except (HTTPError, URLError, TimeoutError):
        pass

    return jsonify({"status": "forwarding_failed"}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
