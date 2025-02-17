import pandas as pd
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def merge_data(
    sentiment_file="data/reddit_sentiment.csv",
    uniswap_file="data/onchain_uniswap_data.csv",
    aave_file="data/onchain_aave_tokens.csv",
    price_file="data/historical_prices.csv",
    output_file="data/merged_data.csv"
):
    """
    Merge sentiment data with on-chain data (Uniswap & Aave) and market prices.
    Ensures all sentiment data is preserved while aligning on-chain & price data.
    """

    try:
        # Check if input files exist
        for file in [sentiment_file, uniswap_file, aave_file, price_file]:
            if not Path(file).exists():
                raise FileNotFoundError(f"Input file not found: {file}")

        # Load datasets
        logging.info("Loading datasets...")
        df_sentiment = pd.read_csv(sentiment_file)
        df_uniswap = pd.read_csv(uniswap_file)
        df_aave = pd.read_csv(aave_file)
        df_prices = pd.read_csv(price_file)

        # Ensure 'timestamp' column exists in all DataFrames
        for df_name, df in {"Sentiment": df_sentiment, "Uniswap": df_uniswap, "Aave": df_aave, "Prices": df_prices}.items():
            if "timestamp" not in df.columns:
                logging.warning(f"⚠️ 'timestamp' column missing in {df_name} data.")
                df["timestamp"] = pd.Series([None] * len(df))  # Fill with NaNs to prevent errors

        # Convert timestamps to datetime where available
        logging.info("Converting timestamps to datetime...")
        for df in [df_sentiment, df_uniswap, df_aave, df_prices]:
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

        # **Merge On-Chain Data (Uniswap & Aave) Using Forward Fill**
        logging.info("Merging Uniswap & Aave data with sentiment...")
        df_merged = df_sentiment.copy()
        if "timestamp" in df_uniswap.columns:
            df_merged = df_merged.merge(df_uniswap, on="timestamp", how="left")
        if "timestamp" in df_aave.columns:
            df_merged = df_merged.merge(df_aave, on="timestamp", how="left")

        # **Merge Market Price Data (Ensure 'close' exists)**
        logging.info("Merging price data...")
        if "timestamp" in df_prices.columns and "close" in df_prices.columns:
            df_merged = df_merged.merge(df_prices[["timestamp", "close"]], on="timestamp", how="left")
        else:
            logging.warning("⚠️ Price data missing 'timestamp' or 'close' column.")

        # **Fill Missing Values Using Forward Fill**
        df_merged.fillna(method="ffill", inplace=True)
        df_merged.fillna(0, inplace=True)  # Ensure no NaN values remain

        # Save merged data
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_merged.to_csv(output_path, index=False)
        logging.info(f"✅ Merged data saved to {output_file} with {len(df_merged)} rows")

    except Exception as e:
        logging.error(f"❌ Error during merge: {e}")
        raise

if __name__ == "__main__":
    merge_data()
