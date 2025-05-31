import os
import json
import csv
from datetime import datetime
from collections import Counter
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # Added for better sentiment analysis

def simple_sentiment_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores['compound']  # Returns a score from -1 (negative) to 1 (positive)

def extract_keywords(text, product, post_count, num_keywords=5):
    # Expanded stop words list
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
        "is", "are", "was", "were", "this", "that", "these", "those",
        "you", "your", "have", "has", "had", "made", "make", "making", "would", "can", "will",
        "i", "me", "my", "we", "us", "our", "they", "them", "their",
        "etsy", "https", "www", "http", "com", "org", "shop", "buy", "sell", "sale",
        "just", "from", "not", "some", "one", "used", "thank", "all", "she", "teacher", "how",
        "off", "there", "love", "beautiful", "handcrafted", "original", "missed", "out", "artist",
        "student", "good", "great", "awesome", "amazing", "wonderful", "nice", "fantastic",
        "excellent", "bad", "terrible", "awful", "poor", "hate", "disappointing", "horrible",
        "worst", "cheap", "broken", "like", "what", "people", "think", "who", "cry", "post",
        "ref", "work", "use", "little", "wondering", "marketplace", "chain", "yarn",
        "discord", "comments", "subreddit", "social", "asking", "please", "rules", "does",
        "about", "more", "because", "get", "items", "wholesale", "price", "silver", "beading",
        "oil", "charms", "reddit", "here", "any", "media", "when", "full", "her", "really",
        "should", "maya", "anyone", "recognizes", "thriftstorehauls", "maker", "green", "neon",
        "item", "tutorial", "set", "crafts",
        # Added more stop words
        "very", "so", "too", "also", "now", "then", "up", "down", "over", "under",
        "it", "its", "he", "him", "his", "as", "be", "been", "being",
        "do", "did", "doing", "say", "said", "go", "went", "gone",
        "know", "knew", "think", "thought", "feel", "felt"
    }
    
    product_words = set()
    base_product_words = product.lower().split()
    for word in base_product_words:
        product_words.add(word)
        if word.endswith("y"):
            product_words.add(word[:-1] + "ies")
        else:
            product_words.add(word + "s")
        if word.startswith("hand"):
            product_words.add(word[4:])
            product_words.add("hand")
        if word == "handmade":
            product_words.add("crafted")
        if word == "jewelry":
            product_words.add("jewellery")
            product_words.add("earrings")
            product_words.add("earring")
        if word == "earrings":
            product_words.add("earring")
        if word == "beeswax":
            product_words.add("wax")
        if word == "painting":
            product_words.add("paint")
            product_words.add("painted")
        if word == "beaded":
            product_words.add("bead")
            product_words.add("beads")
        if word == "soap":
            product_words.add("soapmaking")
    stop_words = stop_words.union(product_words)

    words = re.findall(r'\b\w+\b', text.lower())
    words = [word for word in words if word not in stop_words and len(word) > 3]  # Increased min length to 3
    
    word_counts = Counter(words)
    min_freq = 1 if post_count < 10 else 2
    word_counts = Counter({word: count for word, count in word_counts.items() if count >= min_freq})
    
    descriptive_keywords = {
        "beaded jewelry": ["beads", "necklace", "bracelet", "colors", "style", "design", "gemstone", "pattern"],
        "embroidered textile": ["patterns", "fabric", "thread", "stitch", "design", "colorful", "cotton", "silk"],
        "handmade beeswax candle": ["scent", "wick", "glow", "aroma", "natural", "honey", "burn", "eco"],
        "handmade brass jewelry": ["necklace", "pendant", "shiny", "craft", "vintage", "design", "metal", "polished"],
        "handmade earrings": ["dangle", "stud", "beads", "style", "design", "drop", "hoop", "lightweight"],
        "handmade painting": ["canvas", "colors", "brush", "artwork", "style", "frame", "acrylic", "watercolor"],
        "handmade soap": ["scent", "lather", "organic", "oils", "bar", "natural", "essential", "creamy"],
        "handmade terracotta decor": ["planter", "pot", "sculpture", "decorative", "rustic", "clay", "painted", "ornament"],
        "handmade wooden utensils": ["spoon", "bowl", "carved", "kitchen", "natural", "smooth", "fork", "serving"],
        "handwoven shawl": ["warm", "soft", "traditional", "pattern", "wool", "cotton", "silk", "cozy"],
        "leather bag": ["stitching", "durable", "design", "strap", "style", "pocket", "zipper", "lining"],
        "vegan soap": ["organic", "scent", "lather", "natural", "oils", "cold", "process", "recipe"]
    }
    
    boosted_counts = Counter()
    for word, count in word_counts.items():
        if word in descriptive_keywords.get(product, []):
            boosted_counts[word] = count * 100  # Increased boost factor from 50 to 100
        else:
            boosted_counts[word] = count
    
    top_keywords = [word for word, count in boosted_counts.most_common(num_keywords)]
    while len(top_keywords) < num_keywords:
        top_keywords.append("N/A")
    return top_keywords

def process_trends():
    # Step 1: Load the latest cleaned data file
    input_dir = "data/cleaned"
    cleaned_files = [f for f in os.listdir(input_dir) if f.startswith("cleaned_social_data_") and f.endswith(".json")]
    if not cleaned_files:
        print("Error: No cleaned data files found in data/cleaned/")
        return
    latest_file = max(cleaned_files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)))
    input_file = os.path.join(input_dir, latest_file)

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            cleaned_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in {input_file}. JSONDecodeError: {e}")
        return
    except Exception as e:
        print(f"Error: Failed to read {input_file}. Exception: {e}")
        return

    # Step 2: Handle different possible structures of cleaned_data
    if isinstance(cleaned_data, dict) and "entries" in cleaned_data:
        data = cleaned_data["entries"]
        overall_relevance = cleaned_data.get("overall_relevance", 0.0)
        product_relevance = cleaned_data.get("product_relevance", {})
    elif isinstance(cleaned_data, dict) and "data" in cleaned_data:
        data = cleaned_data["data"]
        overall_relevance = cleaned_data.get("overall_relevance", 0.0)
        product_relevance = cleaned_data.get("product_relevance", {})
        print("Warning: Using 'data' key instead of 'entries' in cleaned data file.")
    elif isinstance(cleaned_data, list):
        data = cleaned_data
        overall_relevance = 0.0
        product_relevance = {}
        print("Warning: Cleaned data is a flat list. Relevance metrics not available.")
    else:
        print(f"Error: Unexpected structure in cleaned data file. Expected a dict with 'entries' or 'data' or a list, got: {type(cleaned_data)}")
        if isinstance(cleaned_data, dict):
            print(f"Available keys: {list(cleaned_data.keys())}")
        return

    # Step 3: Load sales data (now with individual_cost)
    sales_file = "data/sales/sales_data.csv"
    sales_data = {}
    if os.path.exists(sales_file):
        with open(sales_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product = row["product"].strip().lower()
                sales_data[product] = {
                    "individual_cost": float(row["individual_cost"])
                }
    else:
        print("Warning: Sales data file not found. Proceeding without sales data.")

    # Step 4: Process data for each product
    product_stats = {}
    for entry in data:
        text = entry.get("text", "")
        product = entry.get("product", "").strip().lower()
        entry_id = entry.get("id", "")

        if not product or not text or not entry_id:
            continue

        if product not in product_stats:
            product_stats[product] = {"posts": [], "keywords": [], "sentiments": []}

        is_comment = entry_id.startswith("comment_")
        if not is_comment:
            product_stats[product]["posts"].append(text)

        keywords = extract_keywords(text, product, len(product_stats[product]["posts"]))
        product_stats[product]["keywords"].extend(keywords)

        sentiment = simple_sentiment_analysis(text)
        product_stats[product]["sentiments"].append(sentiment)

    # Step 5: Summarize results with structured output
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "processed_trends.csv")

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product", "post_count", "keyword_count", "top_keywords", "sentiment", "product_relevance", "individual_cost", "estimated_monthly_revenue", "estimated_yearly_revenue"])
        
        # Structured console output
        print(f"\nTotal Number of Products: {len(product_stats)}")
        print("Processed Products:")
        print("-" * 50)
        print(f"{'No.':<5} {'Product':<25} {'Posts':<8} {'Keywords':<10} {'Sentiment':<12} {'Relevance':<10} {'Cost':<8} {'Monthly':<10} {'Yearly':<10}")
        print("-" * 50)

        for idx, (product, stats) in enumerate(sorted(product_stats.items()), 1):
            post_count = len(stats["posts"])
            keyword_counts = Counter(stats["keywords"])
            top_keywords = ", ".join(word for word, count in keyword_counts.most_common(5) if word != "N/A")
            keyword_count = len(stats["keywords"])
            avg_sentiment = sum(stats["sentiments"]) / len(stats["sentiments"]) if stats["sentiments"] else 0.0
            sentiment_label = "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"

            # Get individual cost and calculate estimated revenue
            individual_cost = sales_data.get(product, {}).get("individual_cost", 0.0)
            pieces_per_month = 25
            estimated_monthly_revenue = individual_cost * pieces_per_month
            estimated_yearly_revenue = estimated_monthly_revenue * 12

            # Get product relevance
            prod_relevance = product_relevance.get(product, 0.0)

            # Print structured row with $ for currency
            print(f"{idx:<5} {product:<25} {post_count:<8} {keyword_count:<10} {sentiment_label:<12} {prod_relevance:<10.2f}% {'$'+str(individual_cost):<8} {'$'+str(estimated_monthly_revenue):<10} {'$'+str(estimated_yearly_revenue):<10}")

            writer.writerow([product, post_count, keyword_count, top_keywords, avg_sentiment, prod_relevance, individual_cost, estimated_monthly_revenue, estimated_yearly_revenue])

    print("-" * 50)
    print(f"\nOverall Dataset Relevance: {overall_relevance:.2f}%")
    print("\nNote: The estimated monthly and yearly revenues are based on selling 20-30 pieces per month (using 25 pieces as the average). Actual income may vary based on the area where the product is sold, resource availability, and average price in that area.")
    print(f"\nSaved processed trends to {output_file}")

if __name__ == "__main__":
    process_trends()