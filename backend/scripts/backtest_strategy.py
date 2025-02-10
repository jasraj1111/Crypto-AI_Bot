import pandas as pd
import numpy as np
import os

def calculate_atr(prices, period=14):
    """Calculate the Average True Range (ATR) for dynamic stop-loss."""
    prices["high-low"] = prices["high"] - prices["low"]
    prices["high-prev_close"] = abs(prices["high"] - prices["close"].shift(1))
    prices["low-prev_close"] = abs(prices["low"] - prices["close"].shift(1))
    
    # True range is the maximum of these three values
    prices["true_range"] = prices[["high-low", "high-prev_close", "low-prev_close"]].max(axis=1)
    
    # ATR = Simple Moving Average of True Range
    prices["atr"] = prices["true_range"].rolling(window=period, min_periods=1).mean()
    
    return prices

def backtest_trading_strategy(sentiment_file="data/trading_signals.csv", 
                              price_file="data/historical_prices.csv", 
                              output_file="data/backtest_results.csv", 
                              initial_balance=1000, 
                              atr_multiplier=1.5,  # Dynamic stop-loss factor
                              take_profit=0.10):
    """Optimized trading backtest with dynamic ATR stop-loss & take-profit."""

    # Load sentiment data
    try:
        signals = pd.read_csv(sentiment_file)
        print("✅ Loaded sentiment data successfully")
    except FileNotFoundError:
        print(f"❌ Error: {sentiment_file} not found.")
        return

    # Load price data
    try:
        prices = pd.read_csv(price_file)
        print("✅ Loaded price data successfully")
    except FileNotFoundError:
        print(f"❌ Error: {price_file} not found.")
        return

    # Ensure timestamps exist
    if 'timestamp' not in signals.columns:
        print("⚠️ Adding timestamps to sentiment data...")
        signals['timestamp'] = prices['timestamp'].iloc[:len(signals)].values

    # Convert timestamps
    signals['timestamp'] = pd.to_datetime(signals['timestamp'])
    prices['timestamp'] = pd.to_datetime(prices['timestamp'])

    # Calculate ATR for dynamic stop-loss
    prices = calculate_atr(prices)

    # Merge datasets
    data = pd.merge_asof(signals.sort_values("timestamp"), 
                         prices.sort_values("timestamp"), 
                         on="timestamp", direction="forward")

    print(f"✅ Merged data successfully. Shape: {data.shape}")

    # Backtesting logic
    balance = initial_balance
    btc_holdings = 0
    trades = []

    for i, row in data.iterrows():
        if row["signal"] == "BUY" and balance > 0:
            btc_holdings = balance / row["close"]  # Buy BTC
            entry_price = row["close"]  # Store entry price
            dynamic_stop_loss = entry_price - (atr_multiplier * row["atr"])  # Dynamic Stop-Loss
            balance = 0
            trades.append(("BUY", row["timestamp"], row["close"], dynamic_stop_loss))

        elif row["signal"] == "SELL" and btc_holdings > 0:
            balance = btc_holdings * row["close"]  # Sell BTC
            btc_holdings = 0
            trades.append(("SELL", row["timestamp"], row["close"]))

        # Stop-Loss: Sell if price drops below dynamic stop-loss
        if btc_holdings > 0 and row["close"] < dynamic_stop_loss:
            balance = btc_holdings * row["close"]
            btc_holdings = 0
            trades.append(("STOP-LOSS", row["timestamp"], row["close"]))
            print(f"⚠️ Dynamic Stop-Loss triggered at {row['close']:.2f}")

        # Take-Profit: Sell if price rises 10% above entry
        if btc_holdings > 0 and row["close"] > entry_price * (1 + take_profit):
            balance = btc_holdings * row["close"]
            btc_holdings = 0
            trades.append(("TAKE-PROFIT", row["timestamp"], row["close"]))
            print(f"✅ Take-Profit triggered at {row['close']:.2f}")

    # Final balance (sell remaining BTC at last price)
    if btc_holdings > 0:
        balance = btc_holdings * data.iloc[-1]["close"]
        trades.append(("FINAL SELL", data.iloc[-1]["timestamp"], data.iloc[-1]["close"]))

    # Calculate performance
    profit = ((balance - initial_balance) / initial_balance) * 100
    win_rate = sum(1 for trade in trades if trade[0] in ["SELL", "TAKE-PROFIT"] and trade[2] > trades[trades.index(trade)-1][2]) / max(1, len(trades) // 2)

    # Save results
    results_df = pd.DataFrame(trades, columns=["action", "timestamp", "price", "stop_loss"])
    results_df.to_csv(output_file, index=False)

    print(f"\n📈 Trading Results:")
    print(f"✅ Initial Balance: ${initial_balance:.2f}")
    print(f"✅ Final Balance: ${balance:.2f}")
    print(f"✅ Profit/Loss: {profit:.2f}%")
    print(f"✅ Win Rate: {win_rate:.2%}")
    print(f"✅ Total Trades: {len(trades)}")
    print(f"📊 Results saved to {output_file}")

# Run backtest
if __name__ == "__main__":
    backtest_trading_strategy()
