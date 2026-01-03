import os
from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv
import ccxt

load_dotenv()
app = Flask(__name__)
SECRET = os.getenv("WEBHOOK_SECRET")

exchange = ccxt.binanceus({
    "apiKey": os.getenv("BINANCE_API_KEY"),
    "secret": os.getenv("BINANCE_API_SECRET"),
    "enableRateLimit": True
})

def validate_payload(payload):
    """Check if the alert contains everything we need."""
    required_fields = ["side", "symbol", "amount"]

    # Check missing fields
    for field in required_fields:
        if field not in payload:
            return False, f"Missing field: {field}"

    # Check side
    if payload["side"] not in ["buy", "sell"]:
        return False, "Invalid side. Must be 'buy' or 'sell'."

    # Check amount is a number
    try:
        float(payload["amount"])
    except:
        return False, "Amount must be a number."

    # Check symbol format (simple check)
    if "/" not in payload["symbol"]:
        return False, "Symbol must look like 'BTC/USDT'."

    return True, "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    # Check secret header
    if request.headers.get("X-Webhook-Secret") != SECRET:
        abort(401)

    payload = request.json

    # Validate payload
    is_valid, message = validate_payload(payload)
    if not is_valid:
        return jsonify({"error": message}), 400

    side = payload["side"]
    symbol = payload["symbol"]
    amount = float(payload["amount"])

    try:
        if side == "buy":
            exchange.create_market_buy_order(symbol, amount)
        elif side == "sell":
            exchange.create_market_sell_order(symbol, amount)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": "Trade failed"}), 500

if __name__ == "__main__":
    app.run(port=5000)
