import os
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv

# Load NLTK stopwords
nltk.download("stopwords")
nltk.download("punkt")

# Load environment variables
load_dotenv()

# Define stopwords
STOPWORDS = set(stopwords.words("english"))

def clean_text(text):
    """Clean text by removing URLs, special characters, and stopwords."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Remove URLs
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters
    words = word_tokenize(text)  # Tokenize text
    words = [word for word in words if word not in STOPWORDS]  # Remove stopwords
    return " ".join(words)

def preprocess_reddit_data(input_file="data/reddit_data.csv", output_file="data/reddit_cleaned.csv"):
    """Read, clean, and save preprocessed Reddit text data."""
    df = pd.read_csv(input_file)
    
    if "title" not in df.columns:
        print("⚠️ No 'title' column found in CSV. Check the dataset.")
        return

    df["cleaned_text"] = df["title"].astype(str).apply(clean_text)
    
    df[["cleaned_text"]].to_csv(output_file, index=False)
    print(f"✅ Cleaned data saved to {output_file}")

# Run preprocessing
if __name__ == "__main__":
    preprocess_reddit_data()
