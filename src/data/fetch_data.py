import os
import pickle
import json
import pandas as pd
from datetime import datetime
import praw
from dotenv import load_dotenv

def fetch_reddit_data(query, max_posts=50, existing_posts=None, reddit=None):
    if existing_posts is None:
        existing_posts = set()
    cache_file = f"data/cache/{query.replace(' ', '_')}.pkl"
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    
    results, comments = [], []
    # Try year filter first
    try:
        posts = reddit.subreddit(
            "Crafts+Handmade+Soapmaking+Knitting+IndianArt+CandleMaking+Artisan+Art+Etsy+HomeDecor+TextileArts+India+Ceramics+TraditionalArt+SouthAsianArt+FiberArts+DIY+Vintage+InteriorDesign"
        ).search(f'"{query}"', limit=max_posts, sort="relevance", time_filter="year")
        for post in posts:
            post_text = post.title + " " + (post.selftext or "")
            if post_text not in existing_posts and len(post_text) > 30:
                results.append({
                    "id": post.id,
                    "product": query,  # Use query as product
                    "text": post_text,
                    "created_at": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d")
                })
                existing_posts.add(post_text)
                post.comments.replace_more(limit=0)
                for comment in post.comments.list()[:10]:
                    if len(comment.body) > 20:
                        comments.append(comment.body)
    except Exception as e:
        print(f"Error fetching year filter for {query}: {e}")
    
    # If low posts (<5), try all time
    if len(results) < 5:
        try:
            posts = reddit.subreddit(
                "Crafts+Handmade+Soapmaking+Knitting+IndianArt+CandleMaking+Artisan+Art+Etsy+HomeDecor+TextileArts+India+Ceramics+TraditionalArt+SouthAsianArt+FiberArts+DIY+Vintage+InteriorDesign"
            ).search(f'"{query}"', limit=max_posts, sort="relevance", time_filter="all")
            for post in posts:
                post_text = post.title + " " + (post.selftext or "")
                if post_text not in existing_posts and len(post_text) > 30:
                    results.append({
                        "id": post.id,
                        "product": query,
                        "text": post_text,
                        "created_at": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d")
                    })
                    existing_posts.add(post_text)
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:10]:
                        if len(comment.body) > 20:
                            comments.append(comment.body)
        except Exception as e:
            print(f"Error fetching all-time filter for {query}: {e}")
    
    print(f"Fetched {len(results)} posts and {len(comments)} comments for {query}")
    print(f"Posts for {query}:")
    for i, post in enumerate(results, 1):
        print(f"Post {i}: {post['text'][:100]}...")
    print("-" * 50)
    
    # Save to cache
    os.makedirs("data/cache", exist_ok=True)
    with open(cache_file, "wb") as f:
        pickle.dump((results, comments), f)
    
    return results, comments

def fetch_data():
    # Load environment variables
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    
    # Define products
    products = [
        "handmade soap", "handmade scarf", "pottery", "woven basket", "embroidery",
        "wood carving", "beaded jewelry", "leather bag", "brass lamp", "block print",
        "handmade candle", "ceramic", "madhubani", "handmade painting"
    ]
    
    # Fetch data for all products
    all_posts = []
    existing_posts = set()
    for product in products:
        posts, comments = fetch_reddit_data(product, max_posts=50, existing_posts=existing_posts, reddit=reddit)
        all_posts.extend(posts)
        # Include comments as posts for sentiment analysis
        for comment in comments:
            all_posts.append({
                "id": f"comment_{hash(comment)}",
                "product": product,
                "text": comment,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            })
    
    # Save to data/raw/
    output_dir = "data/raw"
    output_file = os.path.join(output_dir, f"raw_social_data_{datetime.now().strftime('%Y%m%d')}.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_posts, f, indent=4)
    print(f"Saved {len(all_posts)} posts/comments to {output_file}")

if __name__ == "__main__":
    fetch_data()