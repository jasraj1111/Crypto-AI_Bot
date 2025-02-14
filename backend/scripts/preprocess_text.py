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
    """Read, clean, and save preprocessed Reddit text data while retaining upvotes, comments, and timestamps."""
    df = pd.read_csv(input_file)
    
    # Check if required columns exist
    required_columns = {"title", "upvotes", "comments", "timestamp"}
    if not required_columns.issubset(df.columns):
        print(f"⚠️ Required columns {required_columns} not found in CSV. Check the dataset.")
        return

    # Clean the text in the 'title' column
    df["cleaned_text"] = df["title"].astype(str).apply(clean_text)
    
    # Save cleaned text along with upvotes, comments, and timestamp
    df[["cleaned_text", "upvotes", "comments", "timestamp"]].to_csv(output_file, index=False)
    print(f"✅ Cleaned data saved to {output_file}")

# Run preprocessing
if __name__ == "__main__":
    preprocess_reddit_data()
