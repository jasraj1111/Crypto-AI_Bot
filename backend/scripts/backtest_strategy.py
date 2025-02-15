import pandas as pd
import numpy as np
from typing import Tuple, List
from datetime import datetime

def backtest_trading_strategy(
    sentiment_file: str = "data/trading_signals.csv",
    price_file: str = "data/historical_prices.csv",
    output_file: str = "data/backtest_results.csv",
    initial_balance: float = 1000,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.1,
    moving_avg_window: int = 20,
    min_confidence: float = 0.6
) -> Tuple[float, float, List]:
    """
    Enhanced trading strategy with risk management and technical indicators.
    
    Args:
        sentiment_file: Path to sentiment signals CSV
        price_file: Path to price data CSV
        output_file: Path to save results
        initial_balance: Starting capital
        stop_loss_pct: Stop loss percentage (default 5%)
        take_profit_pct: Take profit percentage (default 10%)
        moving_avg_window: Window for moving average calculation
        min_confidence: Minimum sentiment confidence to trigger trade
    
    Returns:
        Tuple of (final_balance, ROI, trades_list)
    """
    # Load and prepare data
    signals = pd.read_csv(sentiment_file)
    prices = pd.read_csv(price_file)
    
    signals["timestamp"] = pd.to_datetime(signals["timestamp"])
    prices["timestamp"] = pd.to_datetime(prices["timestamp"])
    
    # Merge datasets
    data = pd.merge_asof(
        signals.sort_values("timestamp"),
        prices.sort_values("timestamp"),
        on="timestamp"
    )
    
    # Add technical indicators
    data["SMA"] = data["close"].rolling(window=moving_avg_window).mean()
    data["STD"] = data["close"].rolling(window=moving_avg_window).std()
    data["Upper_Band"] = data["SMA"] + (data["STD"] * 2)
    data["Lower_Band"] = data["SMA"] - (data["STD"] * 2)
    data["RSI"] = calculate_rsi(data["close"])
    
    # Initialize trading variables
    balance = initial_balance
    btc_holdings = 0
    trades = []
    entry_price = 0
    
    # Trading loop
    for i, row in data.iterrows():
        current_price = row["close"]
        
        # Skip if not enough data for indicators
        if i < moving_avg_window:
            continue
            
        # Check stop loss and take profit if holding position
        if btc_holdings > 0:
            loss_pct = (current_price - entry_price) / entry_price
            
            # Stop loss hit
            if loss_pct <= -stop_loss_pct:
                balance = btc_holdings * current_price
                trades.append(("STOP_LOSS", row["timestamp"], current_price))
                btc_holdings = 0
                continue
                
            # Take profit hit
            if loss_pct >= take_profit_pct:
                balance = btc_holdings * current_price
                trades.append(("TAKE_PROFIT", row["timestamp"], current_price))
                btc_holdings = 0
                continue
        
        # Entry conditions
        if row["signal"] == "BUY" and balance > 0:
            # Additional conditions for buy entry
            if (
                row.get("confidence", 1.0) >= min_confidence and  # Check sentiment confidence
                current_price > row["SMA"] and                    # Price above MA
                row["RSI"] < 70 and                              # Not overbought
                current_price < row["Upper_Band"]                 # Not at upper band
            ):
                btc_holdings = balance / current_price
                balance = 0
                entry_price = current_price
                trades.append(("BUY", row["timestamp"], current_price))
                
        # Exit conditions
        elif row["signal"] == "SELL" and btc_holdings > 0:
            # Additional conditions for sell exit
            if (
                row.get("confidence", 1.0) >= min_confidence or   # High confidence sell signal
                current_price < row["SMA"] or                     # Price below MA
                row["RSI"] > 70 or                               # Overbought
                current_price > row["Upper_Band"]                 # At upper band
            ):
                balance = btc_holdings * current_price
                btc_holdings = 0
                trades.append(("SELL", row["timestamp"], current_price))
    
    # Close any remaining position
    if btc_holdings > 0:
        balance = btc_holdings * data.iloc[-1]["close"]
        trades.append(("SELL", data.iloc[-1]["timestamp"], data.iloc[-1]["close"]))
    
    # Calculate performance metrics
    profit = ((balance - initial_balance) / initial_balance) * 100
    win_rate = calculate_win_rate(trades)
    max_drawdown = calculate_max_drawdown(trades, initial_balance)
    profit_factor = calculate_profit_factor(trades)
    
    # Create DataFrame with trades
    results_df = pd.DataFrame(trades, columns=["action", "timestamp", "price"])
    
    # Calculate trade-specific metrics
    results_df["profit_loss"] = 0.0
    for i in range(1, len(results_df)):
        if results_df.iloc[i]["action"] in ["SELL", "TAKE_PROFIT", "STOP_LOSS"]:
            results_df.iloc[i, results_df.columns.get_loc("profit_loss")] = \
                results_df.iloc[i]["price"] - results_df.iloc[i-1]["price"]
    
    # Calculate cumulative metrics
    results_df["cumulative_profit_loss"] = results_df["profit_loss"].cumsum()
    results_df["running_balance"] = initial_balance + results_df["cumulative_profit_loss"]
    
    # Add summary metrics to a separate DataFrame
    summary_metrics = pd.DataFrame([{
        "metric_name": "Backtest Summary",
        "timestamp": datetime.now(),
        "value": "",
        "details": "Performance Metrics"
    }, {
        "metric_name": "Initial Balance",
        "timestamp": results_df.iloc[0]["timestamp"] if not results_df.empty else None,
        "value": f"${initial_balance:.2f}",
        "details": "Starting capital"
    }, {
        "metric_name": "Final Balance",
        "timestamp": results_df.iloc[-1]["timestamp"] if not results_df.empty else None,
        "value": f"${balance:.2f}",
        "details": "Ending capital"
    }, {
        "metric_name": "Total Return",
        "timestamp": results_df.iloc[-1]["timestamp"] if not results_df.empty else None,
        "value": f"{profit:.2f}%",
        "details": "Return on Investment"
    }, {
        "metric_name": "Win Rate",
        "timestamp": results_df.iloc[-1]["timestamp"] if not results_df.empty else None,
        "value": f"{win_rate:.2%}",
        "details": "Percentage of profitable trades"
    }, {
        "metric_name": "Max Drawdown",
        "timestamp": results_df.iloc[-1]["timestamp"] if not results_df.empty else None,
        "value": f"{max_drawdown:.2%}",
        "details": "Maximum peak to trough decline"
    }, {
        "metric_name": "Profit Factor",
        "timestamp": results_df.iloc[-1]["timestamp"] if not results_df.empty else None,
        "value": f"{profit_factor:.2f}",
        "details": "Ratio of gross profit to gross loss"
    }, {
        "metric_name": "Total Trades",
        "timestamp": results_df.iloc[-1]["timestamp"] if not results_df.empty else None,
        "value": str(len(trades)),
        "details": "Number of trades executed"
    }])
    
    # Combine trades and summary metrics
    final_results = pd.concat([
        summary_metrics,
        results_df.assign(
            metric_name="Trade",
            value=lambda x: x["price"].astype(str),
            details=lambda x: "Trade execution"
        )[["metric_name", "timestamp", "value", "details", "action", "price", "profit_loss", "running_balance"]]
    ]).reset_index(drop=True)
    
    # Save to CSV
    final_results.to_csv(output_file, index=False)
    
    # Print summary
    print(f"✅ Backtesting complete! Final Balance: ${balance:.2f} ({profit:.2f}% ROI)")
    print(f"✅ Win Rate: {win_rate:.2%}")
    print(f"📊 Max Drawdown: {max_drawdown:.2%}")
    print(f"📈 Profit Factor: {profit_factor:.2f}")
    print(f"💾 Results saved to {output_file}")
    
    return balance, profit, trades

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_win_rate(trades: List) -> float:
    """Calculate win rate from trades list."""
    profitable_trades = 0
    total_trades = 0
    
    for i in range(1, len(trades)):
        if trades[i][0] in ["SELL", "TAKE_PROFIT"]:
            total_trades += 1
            if trades[i][2] > trades[i-1][2]:  # Exit price > Entry price
                profitable_trades += 1
                
    return profitable_trades / max(1, total_trades)

def calculate_max_drawdown(trades: List, initial_balance: float) -> float:
    """Calculate maximum drawdown percentage."""
    peak = initial_balance
    max_dd = 0
    
    for trade in trades:
        if trade[0] == "BUY":
            current_value = initial_balance * (trade[2] / trades[0][2])
            max_dd = min(max_dd, (current_value - peak) / peak)
            peak = max(peak, current_value)
            
    return abs(max_dd)

def calculate_profit_factor(trades: List) -> float:
    """Calculate profit factor (gross profit / gross loss)."""
    gross_profit = 0
    gross_loss = 0
    
    for i in range(1, len(trades)):
        if trades[i][0] in ["SELL", "TAKE_PROFIT", "STOP_LOSS"]:
            profit = trades[i][2] - trades[i-1][2]
            if profit > 0:
                gross_profit += profit
            else:
                gross_loss += abs(profit)
                
    return gross_profit / max(gross_loss, 1)

if __name__ == "__main__":
    backtest_trading_strategy()