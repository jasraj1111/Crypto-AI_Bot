from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Load trading signals
def load_signals():
    try:
        df = pd.read_csv("scripts/data/trading_signals.csv")
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.route("/api/trade-signals", methods=["GET"])
def get_trade_signals():
    """API to fetch latest trading signals."""
    signals = load_signals()
    return jsonify(signals)

@app.route("/api/backtest-results", methods=["GET"])
def get_backtest_results():
    """API to fetch latest backtesting results."""
    try:
        df = pd.read_csv("scripts/data/backtest_results.csv")
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/")
def home():
    return "Flask app is running!"

if __name__ == "__main__":
    app.run(debug=True, port=5000)


# http://localhost:5000/api/trade-signals
# http://localhost:5000/api/backtest-results