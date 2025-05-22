import os
import pickle
import praw
from dotenv import load_dotenv

load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="MicroEntrepreneurForecaster/0.1"
)
subreddit = reddit.subreddit("Crafts+Handmade+Soapmaking+Knitting+IndianArt+CandleMaking+Artisan+Art+Etsy+HomeDecor+TextileArts+India+Ceramics+TraditionalArt+SouthAsianArt+FiberArts+DIY+Vintage+InteriorDesign")

def fetch_x_posts(query, max_posts=50, existing_posts=None):
    if existing_posts is None:
        existing_posts = set()
    cache_file = f"data/cache/{query.replace(' ', '_')}.pkl"
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    results, comments = [], []
    # Try year filter first
    posts = subreddit.search(f'"{query}"', limit=max_posts, sort="relevance", time_filter="year")
    for post in posts:
        post_text = post.title + " " + (post.selftext or "")
        if post_text not in existing_posts and len(post_text) > 30:
            results.append(post_text)
            existing_posts.add(post_text)
            post.comments.replace_more(limit=0)
            for comment in post.comments.list()[:10]:
                if len(comment.body) > 20:
                    comments.append(comment.body)
    # If low posts (<5), try all time
    if len(results) < 5:
        posts = subreddit.search(f'"{query}"', limit=max_posts, sort="relevance", time_filter="all")
        for post in posts:
            post_text = post.title + " " + (post.selftext or "")
            if post_text not in existing_posts and len(post_text) > 30:
                results.append(post_text)
                existing_posts.add(post_text)
                post.comments.replace_more(limit=0)
                for comment in post.comments.list()[:10]:
                    if len(comment.body) > 20:
                        comments.append(comment.body)
    print(f"Fetched {len(results)} posts and {len(comments)} comments for {query}")
    print(f"Posts for {query}:")
    for i, post in enumerate(results, 1):
        print(f"Post {i}: {post[:100]}...")
    print("-" * 50)
    with open(cache_file, "wb") as f:
        pickle.dump((results, comments), f)
    return results, comments

if __name__ == "__main__":
    products = ["handmade soap", "handmade scarf", "pottery", "woven basket", "embroidery",
                "wood carving", "beaded jewelry", "leather bag", "brass lamp", "block print",
                "handmade candle", "ceramic", "madhubani", "handmade painting"]
    for product in products:
        fetch_x_posts(product)