import ccxt
import pandas as pd

def fetch_crypto_prices(symbol="BTC/USDT", timeframe="1h", limit=1000):
    """Fetch historical crypto price data from Binance."""
    binance = ccxt.binance()
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")  # Convert to readable date
    df.to_csv("data/historical_prices.csv", index=False)
    
    print(f"✅ {len(df)} historical price records saved.")

if __name__ == "__main__":
    fetch_crypto_prices()


