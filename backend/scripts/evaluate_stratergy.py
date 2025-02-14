import pandas as pd
import numpy as np

def evaluate_strategy(backtest_results="data/backtest_results.csv", initial_balance=1000):
    """Evaluate the trading strategy's accuracy and profitability."""

    # Load backtest results
    try:
        df = pd.read_csv(backtest_results)
        if df.empty:
            print("❌ No trades executed. Check strategy conditions.")
            return
    except FileNotFoundError:
        print(f"❌ Error: {backtest_results} file not found.")
        return
    
    # Ensure required columns exist
    required_columns = ["action", "timestamp", "price"]
    if not all(col in df.columns for col in required_columns):
        print(f"❌ Missing required columns {required_columns} in results file.")
        return

    # Calculate Total Return (ROI %)
    final_balance = df.iloc[-1]["price"] if "FINAL SELL" in df["action"].values else initial_balance
    roi = ((final_balance - initial_balance) / initial_balance) * 100

    # Count profitable trades (Win Rate)
    wins = sum(1 for i in range(1, len(df)) if df.iloc[i]["action"] in ["SELL", "TAKE-PROFIT"] and df.iloc[i]["price"] > df.iloc[i-1]["price"])
    total_trades = len(df) // 2  # Every Buy-Sell pair counts as one trade
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

    # Calculate Sharpe Ratio (Risk-Adjusted Return)
    returns = df["price"].pct_change().dropna()
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

    # Calculate Max Drawdown (Worst Loss)
    rolling_max = df["price"].cummax()
    drawdown = (rolling_max - df["price"]) / rolling_max
    max_drawdown = drawdown.max() * 100  # Convert to percentage

    # Calculate Profit Factor (Total Profit / Total Loss)
    profit_trades = [df.iloc[i]["price"] - df.iloc[i-1]["price"] for i in range(1, len(df)) if df.iloc[i]["action"] in ["SELL", "TAKE-PROFIT"] and df.iloc[i]["price"] > df.iloc[i-1]["price"]]
    loss_trades = [df.iloc[i-1]["price"] - df.iloc[i]["price"] for i in range(1, len(df)) if df.iloc[i]["action"] == "STOP-LOSS" and df.iloc[i]["price"] < df.iloc[i-1]["price"]]
    
    total_profit = sum(profit_trades)
    total_loss = sum(loss_trades)
    profit_factor = (total_profit / abs(total_loss)) if total_loss != 0 else float('inf')

    # Display Results
    print("\n📈 **Trading Strategy Performance:**")
    print(f"✅ ROI (%): {roi:.2f}%")
    print(f"✅ Win Rate: {win_rate:.2f}%")
    print(f"✅ Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"✅ Max Drawdown: {max_drawdown:.2f}%")
    print(f"✅ Profit Factor: {profit_factor:.2f}")
    print(f"✅ Total Trades Executed: {total_trades}")

# Run Evaluation
if __name__ == "__main__":
    evaluate_strategy()
