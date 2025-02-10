import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_trading_signals(input_file="data/reddit_sentiment.csv", output_file="data/trading_signals.csv", window=10):
    """Generate Buy/Sell/Hold signals based on Reddit sentiment trends."""

    df = pd.read_csv(input_file)

    if "sentiment_label" not in df.columns:
        print("⚠️ No 'sentiment_label' column found. Run sentiment analysis first.")
        return

    # Convert sentiment to numerical values
    df["bullish"] = (df["sentiment_label"] == "bullish").astype(int)
    df["bearish"] = (df["sentiment_label"] == "bearish").astype(int)

    # Calculate rolling sentiment trend (last 'window' posts)
    df["bullish_trend"] = df["bullish"].rolling(window=window, min_periods=1).mean()
    df["bearish_trend"] = df["bearish"].rolling(window=window, min_periods=1).mean()

    # Generate Buy/Sell/Hold signals
    df["signal"] = df.apply(
        lambda row: "BUY" if row["bullish_trend"] > 0.6 else 
                    "SELL" if row["bearish_trend"] > 0.6 else "HOLD", 
        axis=1
    )

    # Save signals to file
    df[["sentiment_label", "bullish_trend", "bearish_trend", "signal"]].to_csv(output_file, index=False)
    print(f"✅ Trading signals saved to {output_file}")

# Run trading signal generation
if __name__ == "__main__":
    generate_trading_signals()
