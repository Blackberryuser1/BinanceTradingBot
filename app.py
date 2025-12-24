import os
from flask import Flask, request, abort
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

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("X-Webhook-Secret") != SECRET:
        abort(401)

    payload = request.json
    side = payload.get("side")
    symbol = payload.get("symbol")
    amount = payload.get("amount")

    try:
        if side == "buy":
            exchange.create_market_buy_order(symbol, amount)
        elif side == "sell":
            exchange.create_market_sell_order(symbol, amount)
        return {"status": "ok"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(port=5000)