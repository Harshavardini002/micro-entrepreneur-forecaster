import os
import json
import pickle
import praw
import time
from datetime import datetime
from dotenv import load_dotenv

def fetch_reddit_data(query, product_name, max_posts=300, existing_posts=None, reddit=None):
    if existing_posts is None:
        existing_posts = set()
    cache_file = f"data/cache/{query.replace(' ', '_')}_top.pkl"
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    
    # Descriptive terms to ensure relevance
    descriptive_terms = [
        "handmade", "artisan", "craft", "diy", "organic", "vegan", "natural", "traditional",
        "authentic", "rustic", "unique", "custom", "for sale", "buy", "shop", "etsy", "made", "create", "design"
    ]
    
    # Product-specific keywords
    product_keywords = product_name.lower().split()
    
    results, comments = [], []
    # Subreddit selection for high-data products
    base_subreddits = (
        "Crafts+Handmade+Soapmaking+Artisan+Art+Etsy+HomeDecor+DIY+RedditMade+SmallBusiness+"
        "SomethingIMade+HandmadeGifts+JewelryMaking+Beading+Leathercraft+ArtMarket+Watercolor"
    )
    
    try:
        posts = reddit.subreddit(base_subreddits).search(f'"{query}"', limit=max_posts, sort="relevance", time_filter="all")
        for post in posts:
            post_text = post.title + " " + (post.selftext or "")
            post_lower = post_text.lower()
            if (post_text not in existing_posts and
                len(post_text) > 20 and
                (any(keyword in post_lower for keyword in product_keywords) or
                 any(term in post_lower for term in descriptive_terms))):
                results.append({
                    "id": post.id,
                    "product": product_name,
                    "text": post_text,
                    "created_at": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d")
                })
                existing_posts.add(post_text)
                post.comments.replace_more(limit=0)
                for comment in post.comments.list()[:30]:
                    comment_lower = comment.body.lower()
                    if (len(comment.body) > 20 and
                        (any(keyword in comment_lower for keyword in product_keywords) or
                         any(term in comment_lower for term in descriptive_terms)) and
                        not any(generic in comment_lower for generic in ["nice", "great", "thanks", "love it", "cool", "awesome"])):
                        comments.append(comment.body)
        time.sleep(2)
    except Exception as e:
        print(f"Error fetching data for {query}: {e}")
        time.sleep(5)
    
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

def fetch_top_products():
    # Load environment variables
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    
    # Start fresh
    all_posts = []
    existing_posts = set()
    
    # Define queries for high-data products only
    search_queries = [
        ("beaded jewelry", "beaded jewelry"),
        ("handmade beaded jewelry", "beaded jewelry"),
        ("artisan beaded jewelry", "beaded jewelry"),
        ("handmade earrings", "handmade earrings"),
        ("artisan earrings", "handmade earrings"),
        ("handcrafted earrings", "handmade earrings"),
        ("handmade painting", "handmade painting"),
        ("artisan painting", "handmade painting"),
        ("handcrafted painting", "handmade painting"),
        ("handmade soap", "handmade soap"),
        ("artisan soap", "handmade soap"),
        ("handcrafted soap", "handmade soap"),
        ("leather bag", "leather bag"),
        ("handmade leather bag", "leather bag"),
        ("artisan leather bag", "leather bag"),
    ]
    
    # Fetch data for all queries
    for query, product_name in search_queries:
        posts, comments = fetch_reddit_data(query, product_name, max_posts=300, existing_posts=existing_posts, reddit=reddit)
        all_posts.extend(posts)
        for comment in comments:
            all_posts.append({
                "id": f"comment_{hash(comment)}",
                "product": product_name,
                "text": comment,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            })
    
    # Save data
    output_dir = "data/raw"
    output_file = os.path.join(output_dir, f"raw_social_data_{datetime.now().strftime('%Y%m%d')}.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_posts, f, indent=4)
    print(f"Saved {len(all_posts)} posts/comments to {output_file}")

if __name__ == "__main__":
    fetch_top_products()