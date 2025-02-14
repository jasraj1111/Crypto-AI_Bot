import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_trading_signals(input_file="data/reddit_sentiment.csv", output_file="data/trading_signals.csv", window=10):
    """Generate Buy/Sell/Hold signals based on Reddit sentiment trends."""

    # Load the data
    df = pd.read_csv(input_file)

    # Debugging: Print columns to verify
    print("Columns in the input file:", df.columns)

    # Check if 'sentiment_label' column exists
    if "sentiment_label" not in df.columns:
        print("⚠️ No 'sentiment_label' column found. Run sentiment analysis first.")
        return

    # Check if 'timestamp' column exists (or an alternative name)
    timestamp_column = "timestamp"  # Default column name
    if timestamp_column not in df.columns:
        # Look for alternative column names (e.g., 'date', 'time', 'created_at')
        possible_timestamp_columns = ["date", "time", "created_at", "datetime"]
        for col in possible_timestamp_columns:
            if col in df.columns:
                timestamp_column = col
                print(f"⚠️ 'timestamp' column not found. Using '{col}' as the timestamp column.")
                break
        else:
            raise KeyError(f"No timestamp column found. Expected one of: {['timestamp'] + possible_timestamp_columns}")

    # Convert timestamp to datetime (if not already)
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_column]):
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])

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
    df[[timestamp_column, "sentiment_label", "bullish_trend", "bearish_trend", "signal"]].to_csv(output_file, index=False)
    print(f"✅ Trading signals saved to {output_file}")

# Run trading signal generation
if __name__ == "__main__":
    generate_trading_signals()