import os
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from dotenv import load_dotenv

# Download NLTK resources
nltk.download("vader_lexicon")
nltk.download("stopwords")
nltk.download("wordnet")

# Load environment variables
load_dotenv()

# Initialize VADER Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Add crypto-specific terms to VADER lexicon
crypto_lexicon = {
    "hodl": 0.8,  # Positive sentiment
    "fud": -0.8,  # Negative sentiment
    "moon": 0.9,  # Positive sentiment
    "rekt": -0.9,  # Negative sentiment
}
sia.lexicon.update(crypto_lexicon)

def preprocess_text(text):
    """Preprocess text by removing noise, stopwords, and lemmatizing."""
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    # Convert to lowercase
    text = text.lower()
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    text = " ".join([word for word in text.split() if word not in stop_words])
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    text = " ".join([lemmatizer.lemmatize(word) for word in text.split()])
    return text

def analyze_sentiment(input_file="data/reddit_cleaned.csv", output_file="data/reddit_sentiment.csv"):
    """Analyze sentiment of Reddit posts using VADER while retaining upvotes, comments, and timestamps."""
    df = pd.read_csv(input_file)
    
    # Check if required columns exist
    required_columns = {"cleaned_text", "upvotes", "comments", "timestamp"}
    if not required_columns.issubset(df.columns):
        print(f"⚠️ Required columns {required_columns} not found in CSV. Check preprocessing.")
        return

    # Preprocess text
    df["cleaned_text"] = df["cleaned_text"].astype(str).apply(preprocess_text)

    # Apply VADER sentiment analysis
    df["sentiment_score"] = df["cleaned_text"].apply(lambda text: sia.polarity_scores(text)["compound"])
    
    # Classify sentiment using dynamic thresholds
    lower_threshold = df["sentiment_score"].quantile(0.25)
    upper_threshold = df["sentiment_score"].quantile(0.75)
    df["sentiment_label"] = df["sentiment_score"].apply(
        lambda score: "bullish" if score > upper_threshold else 
                      "bearish" if score < lower_threshold else 
                      "bullish" if df.loc[df["sentiment_score"] == score, "upvotes"].values[0] > 10 else "bearish"
    )

    # Save results with upvotes, comments, and timestamp
    df[["cleaned_text", "upvotes", "comments", "timestamp", "sentiment_score", "sentiment_label"]].to_csv(output_file, index=False)
    print(f"✅ Sentiment analysis complete! Saved to {output_file}")

# Run sentiment analysis
if __name__ == "__main__":
    analyze_sentiment()
