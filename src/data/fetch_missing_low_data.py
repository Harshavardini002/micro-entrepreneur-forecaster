import os
import json
import pickle
import praw
import time
from datetime import datetime
from dotenv import load_dotenv

def fetch_reddit_data(query, product_name, max_posts=500, max_comments=100, existing_posts=None, reddit=None):
    if existing_posts is None:
        existing_posts = set()
    cache_file = f"data/cache/{query.replace(' ', '_')}_missing_low.pkl"
    
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
    base_subreddits = (
        "Crafts+Handmade+Knitting+IndianArt+Artisan+Art+Etsy+HomeDecor+TextileArts+Ceramics+TraditionalArt+"
        "SouthAsianArt+FiberArts+DIY+Vintage+RedditMade+SmallBusiness+SomethingIMade+HandmadeGifts+"
        "KnittingPatterns+Crochet+PotteryStudio+CeramicArt+TextileDesign+IndianFashion+VintageDecor+"
        "CandleMakers+Woodworking+Carving+Soapmakers+NaturalBeauty+ArtMarket+DIYGifts+Crafty+"
        "ThriftStoreHauls+Frugal+Anticonsumption+SustainableLiving+Minimalism+Decor+InteriorDesign+"
        "Jewelry+Quilting+Sustainable"
    )
    
    try:
        posts = reddit.subreddit(base_subreddits).search(f'"{query}"', limit=max_posts, sort="relevance", time_filter="all")
        for post in posts:
            post_text = post.title + " " + (post.selftext or "")
            post_lower = post_text.lower()
            if (post_text not in existing_posts and
                len(post_text) > 5 and
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
                for comment in post.comments.list()[:max_comments]:
                    comment_lower = comment.body.lower()
                    if (len(comment.body) > 5 and
                        (any(keyword in comment_lower for keyword in product_keywords) or
                         any(term in comment_lower for term in descriptive_terms))):
                        comments.append(comment.body)
        time.sleep(3)
    except Exception as e:
        print(f"Error fetching data for {query}: {e}")
        time.sleep(10)
    
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

def fetch_missing_low_data():
    # Load environment variables
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    
    # Start fresh instead of loading existing data
    all_posts = []
    
    # Define search queries for new alternative products and embroidered textile
    search_queries = [
        # Handmade Brass Jewelry (replacing Brass Lamp)
        ("Handmade Brass Bangles", "handmade brass jewelry"),
        ("Brass Necklace", "handmade brass jewelry"),
        ("Artisan Brass Jewelry", "handmade brass jewelry"),
        ("handmade brass", "handmade brass jewelry"),
        # Handmade Beeswax Candle (replacing Handmade Candle)
        ("Handmade Beeswax Candle", "handmade beeswax candle"),
        ("Beeswax Candle", "handmade beeswax candle"),
        ("Eco-Friendly Beeswax Candle", "handmade beeswax candle"),
        ("natural beeswax candle", "handmade beeswax candle"),
        # Handwoven Shawl (replacing Handmade Scarf)
        ("Handwoven Shawl", "handwoven shawl"),
        ("Pashmina Shawl", "handwoven shawl"),
        ("Traditional Handwoven Shawl", "handwoven shawl"),
        ("handmade shawl", "handwoven shawl"),
        # Handmade Terracotta Decor (replacing Pottery)
        ("Handmade Terracotta Planter", "handmade terracotta decor"),
        ("Terracotta Figurine", "handmade terracotta decor"),
        ("Rustic Terracotta Decor", "handmade terracotta decor"),
        ("terracotta craft", "handmade terracotta decor"),
        # Handmade Wooden Utensils (replacing Wood Carving)
        ("Handmade Wooden Spoon", "handmade wooden utensils"),
        ("Wooden Bowl", "handmade wooden utensils"),
        ("Eco-Friendly Wooden Utensils", "handmade wooden utensils"),
        ("handmade wooden kitchen", "handmade wooden utensils"),
        # Embroidered Textile (keeping for now, with broader keywords)
        ("Hand Embroidery", "embroidered textile"),
        ("Floral Embroidery", "embroidered textile"),
        ("Minimalist Embroidery", "embroidered textile"),
        ("embroidered fabric", "embroidered textile"),
        ("handmade embroidery", "embroidered textile"),
        # Vegan Soap (already sufficient, but included for consistency)
        ("Cold Process Soap", "vegan soap"),
        ("Essential Oil Soap", "vegan soap"),
        ("Zero Waste Soap", "vegan soap"),
    ]
    
    # Fetch data using the new queries
    existing_posts = set()
    for query, product_name in search_queries:
        print(f"Fetching data for {product_name} using query: {query}")
        posts, comments = fetch_reddit_data(query, product_name, max_posts=500, max_comments=100, existing_posts=existing_posts, reddit=reddit)
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"raw_social_data_low_{timestamp}.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_posts, f, indent=4)
    print(f"Saved {len(all_posts)} posts/comments to {output_file}")

if __name__ == "__main__":
    fetch_missing_low_data()