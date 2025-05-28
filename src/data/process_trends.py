import json
import pandas as pd
import os
from src.utils.text_processing import preprocess_text, get_sentiment

def process_trends():
    input_dir = "data/raw"
    output_file = "data/processed/processed_trends.csv"
    
    # Find the latest raw data file
    raw_files = [f for f in os.listdir(input_dir) if f.startswith("raw_social_data_") and f.endswith(".json")]
    if not raw_files:
        print("Error: No raw data files found in data/raw/")
        return
    latest_file = max(raw_files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)))
    input_file = os.path.join(input_dir, latest_file)
    
    # Load raw data
    with open(input_file, "r") as f:
        data = json.load(f)
    
    # Process data
    results = []
    # Map of simple keywords to full product names
    product_mapping = {
        "soap": "handmade soap",
        "soaps": "handmade soap",
        "shampoo": "handmade soap",
        "bar": "handmade soap",
        "scarf": "handmade scarf",
        "scarves": "handmade scarf",
        "shawl": "handmade scarf",
        "wrap": "handmade scarf",
        "pottery": "pottery",
        "ceramic": "pottery",
        "vase": "pottery",
        "bowl": "pottery",
        "plate": "pottery",
        "mug": "pottery",
        "cup": "pottery",
        "basket": "handwoven basket",
        "baskets": "handwoven basket",
        "woven": "handwoven basket",
        "weave": "handwoven basket",
        "textile": "embroidered textile",
        "shawl": "embroidered textile",
        "saree": "embroidered textile",
        "cloth": "embroidered textile",
        "weaving": "embroidered textile",
        "carving": "wood carving",
        "sculpture": "wood carving",
        "wooden": "wood carving",
        "woodwork": "wood carving",
        "jewelry": "beaded jewelry",
        "necklace": "beaded jewelry",
        "bracelet": "beaded jewelry",
        "bead": "beaded jewelry",
        "beads": "beaded jewelry",
        "pendant": "beaded jewelry",
        "ring": "beaded jewelry",
        "bag": "leather bag",
        "handbag": "leather bag",
        "purse": "leather bag",
        "tote": "leather bag",
        "wallet": "leather bag",
        "lamp": "brass lamp",
        "light": "brass lamp",
        "lantern": "brass lamp",
        "lighting": "brass lamp",
        "fabric": "block printed fabric",
        "print": "block printed fabric",
        "printed": "block printed fabric",
        "textile": "block printed fabric",
        "cloth": "block printed fabric",
        "candle": "handmade candle",
        "candles": "handmade candle",
        "wax": "handmade candle",
        "tableware": "ceramic tableware",
        "plates": "ceramic tableware",
        "bowls": "ceramic tableware",
        "dishes": "ceramic tableware",
        "dish": "ceramic tableware",
        "madhubani": "madhubani painting",
        "mithila": "madhubani painting",
        "painting": "handmade painting",
        "artwork": "handmade painting",
        "art": "handmade painting",
        "canvas": "handmade painting",
        "sketch": "handmade painting",
        "drawing": "handmade painting",
        "earring": "handmade earrings",
        "earrings": "handmade earrings",
        "studs": "handmade earrings",
        "dangles": "handmade earrings",
        "hoop": "handmade earrings",
        "drop": "handmade earrings"
    }
    
    for post in data:
        # Since post is a string, use it directly
        if not isinstance(post, str):
            continue  # Skip non-string entries, just in case
        tokens = preprocess_text(post)
        # Find the product by checking if any token or post text contains a product keyword
        product = None
        post_lower = post.lower()
        # First, try matching tokens
        for token in tokens:
            for key, prod in product_mapping.items():
                if key in token:
                    product = prod
                    break
            if product:
                break
        # Fallback: check the raw post text
        if not product:
            for key, prod in product_mapping.items():
                if key in post_lower:
                    product = prod
                    break
        if not product:
            continue  # Skip posts where no product is identified
        
        sentiment = get_sentiment(post)
        results.append({
            "product": product,
            "keyword_count": len(tokens),
            "sentiment_score": sentiment,
            "post_count": 1
        })
    
    # Aggregate by product
    df = pd.DataFrame(results)
    df = df.groupby("product").agg({
        "keyword_count": "sum",
        "sentiment_score": "mean",
        "post_count": "sum"
    }).reset_index()
    
    # Save to data/processed/
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Saved processed trends to {output_file}")
    for _, row in df.iterrows():
        print(f"Processed {row['product']}: {row['post_count']} posts, {row['keyword_count']} keywords, sentiment {row['sentiment_score']:.2f}")

if __name__ == "__main__":
    process_trends()