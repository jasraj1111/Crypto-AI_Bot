import pandas as pd
import numpy as np
from backtest_strategy import backtest_trading_strategy

# Hyperparameter ranges
atr_multipliers = [1.5, 2.0, 2.5, 3.0]  # ATR stop-loss factors
take_profits = [0.05, 0.10, 0.15]  # Take-profit levels (5%, 10%, 15%)
risk_per_trades = [0.01, 0.02]  # Risk 1% or 2% of balance per trade
rsi_lowers = [30, 40]  # RSI lower thresholds for uptrend confirmation
rsi_uppers = [60, 70]  # RSI upper thresholds for downtrend confirmation

# Store results
results = []

# Ensure data files exist before running
try:
    sentiment_file = "data/reddit_sentiment.csv"
    price_file = "data/historical_prices.csv"
    sentiment_data = pd.read_csv(sentiment_file)
    price_data = pd.read_csv(price_file)
    print("✅ Data loaded successfully.")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

# Loop through hyperparameter combinations
for atr in atr_multipliers:
    for tp in take_profits:
        for risk in risk_per_trades:
            for rsi_lower in rsi_lowers:
                for rsi_upper in rsi_uppers:
                    print(f"🔄 Testing ATR Multiplier: {atr}, Take-Profit: {tp*100}%, Risk per Trade: {risk*100}%, RSI Lower: {rsi_lower}, RSI Upper: {rsi_upper}")
                    
                    try:
                        # Run backtest with current hyperparameters
                        backtest_trading_strategy(
                            sentiment_file=sentiment_file,
                            price_file=price_file,
                            output_file="data/backtest_results.csv",
                            initial_balance=1000,
                            risk_per_trade=risk,
                            atr_multiplier=atr,
                            take_profit=tp,
                            rsi_lower=rsi_lower,
                            rsi_upper=rsi_upper
                        )

                        # Load results and extract performance metrics
                        results_df = pd.read_csv("data/backtest_results.csv")
                        
                        # Check if DataFrame is empty or missing required columns
                        if results_df.empty or "price" not in results_df.columns:
                            print("⚠️ No results found or 'price' column missing. Skipping this combination.")
                            continue

                        final_balance = results_df.iloc[-1]["price"]
                        roi = ((final_balance - 1000) / 1000) * 100
                        total_trades = len(results_df)

                        # Calculate additional metrics
                        returns = results_df["price"].pct_change().dropna()
                        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if not returns.std() == 0 else 0
                        max_drawdown = (results_df["price"].cummax() - results_df["price"]).max()

                        results.append({
                            "ATR Multiplier": atr,
                            "Take-Profit (%)": tp * 100,
                            "Risk per Trade (%)": risk * 100,
                            "RSI Lower": rsi_lower,
                            "RSI Upper": rsi_upper,
                            "Final Balance": final_balance,
                            "ROI (%)": roi,
                            "Total Trades": total_trades,
                            "Sharpe Ratio": sharpe_ratio,
                            "Max Drawdown": max_drawdown
                        })

                    except Exception as e:
                        print(f"❌ Error occurred with ATR={atr}, TP={tp}, Risk={risk}, RSI Lower={rsi_lower}, RSI Upper={rsi_upper}: {e}")

# Convert results to DataFrame and save
if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv("data/hyperparameter_optimization_results.csv", index=False)
    print("\n✅ Hyperparameter tuning complete! Results saved to data/hyperparameter_optimization_results.csv")
    print(results_df)
else:
    print("\n❌ No results to save. Check for errors in the backtesting process.")
