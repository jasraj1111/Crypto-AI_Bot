import praw
import os
import pandas as pd
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Initialize Reddit API client
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=USER_AGENT)

def fetch_reddit_posts(subreddit_name="cryptocurrency", limit=10):
    """Fetch top posts from a subreddit."""
    subreddit = reddit.subreddit(subreddit_name)
    posts = [{"title": post.title, "score": post.score, "comments": post.num_comments} for post in subreddit.hot(limit=limit)]
    df = pd.DataFrame(posts)
    df.to_csv("data/reddit_data.csv")
    print(f"✅ {len(df)} posts saved to reddit_data.csv")

# Example usage
if __name__ == "__main__":
    fetch_reddit_posts()
