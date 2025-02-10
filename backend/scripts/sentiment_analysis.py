import os
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Download VADER model
nltk.download("vader_lexicon")

# Load environment variables
load_dotenv()

# Initialize VADER Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(input_file="data/reddit_cleaned.csv", output_file="data/reddit_sentiment.csv"):
    """Analyze sentiment of Reddit posts using VADER."""
    df = pd.read_csv(input_file)
    
    if "cleaned_text" not in df.columns:
        print("⚠️ No 'cleaned_text' column found in CSV. Check preprocessing.")
        return

    # Apply VADER sentiment analysis
    df["sentiment_score"] = df["cleaned_text"].astype(str).apply(lambda text: sia.polarity_scores(text)["compound"])
    
    # Classify sentiment
    df["sentiment_label"] = df["sentiment_score"].apply(lambda score: "bullish" if score > 0.05 else "bearish" if score < -0.05 else "neutral")

    # Save results
    df.to_csv(output_file, index=False)
    print(f"✅ Sentiment analysis complete! Saved to {output_file}")

# Run sentiment analysis
if __name__ == "__main__":
    analyze_sentiment()
