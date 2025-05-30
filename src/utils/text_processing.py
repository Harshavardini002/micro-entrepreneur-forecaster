import os
import json
import pandas as pd
from textblob import TextBlob
from collections import Counter
import re
from datetime import datetime

def text_processing():
    # Step 1: Load the latest raw data file
    input_dir = "data/raw"
    print(f"Listing files in {input_dir}:")
    all_files = os.listdir(input_dir)
    print(all_files)
    
    raw_files = [f for f in all_files if f.startswith("raw_social_data_") and f.endswith(".json")]
    
    if not raw_files:
        print("Error: No raw data files found in data/raw/")
        return
    
    latest_file = max(raw_files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)))
    input_file = os.path.join(input_dir, latest_file)
    
    print(f"Fetching file: {input_file}")
    try:
        with open(input_file, "r") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return
    
    print(f"Loaded {len(raw_data)} entries from 1 file")
    
    # Define all products to ensure they are included
    all_products = [
        "beaded jewelry", "handmade earrings", "handmade painting", "handmade soap",
        "leather bag", "handmade brass jewelry", "handmade beeswax candle",
        "handwoven shawl", "handmade terracotta decor", "handmade wooden utensils",
        "embroidered textile", "vegan soap"
    ]
    
    # Step 2: Analyze keywords, sentiment, and compute popularity
    product_stats = {}
    all_texts = []
    
    for entry in raw_data:
        product = entry["product"]
        text = entry["text"]
        
        # Initialize product stats
        if product not in product_stats:
            product_stats[product] = {"texts": [], "all_words": [], "sentiments": []}
        
        # Clean text: Remove punctuation except spaces, convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower()).strip()
        text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces to single space
        product_stats[product]["texts"].append(text)
        all_texts.append(text)
        
        # Store words for keyword diversity
        words = text.split()
        product_stats[product]["all_words"].extend(words)
        
        # Calculate sentiment
        sentiment = TextBlob(text).sentiment.polarity  # -1 to 1 scale
        product_stats[product]["sentiments"].append(sentiment)
    
    # Ensure all products are in product_stats
    for product in all_products:
        if product not in product_stats:
            product_stats[product] = {"texts": [], "all_words": [], "sentiments": []}
    
    # Step 3: Summarize keywords, relevance, sentiment, and popularity
    analysis_data = {"product_stats": {}, "keywords": []}
    
    # Expanded stop words list to exclude boring words and platform terms
    stop_words = {
        "i", "the", "a", "and", "to", "of", "is", "in", "for", "on",
        "have", "your", "they", "just", "it", "that", "this", "with",
        "are", "you", "at", "but", "my", "was", "so", "be", "not",
        "all", "can", "from", "as", "or", "if", "me", "like", "handmade",
        "product", "products", "etsy", "com", "shop", "s", "t", "https",
        "www", "http", "m", "off", "code", "coupon", "nice", "great",
        "thanks", "love it", "cool", "awesome"
    }
    
    # Define variations for product tokens
    token_variations = {
        "jewelry": ["jewelry", "jewellery", "jewelrymaking", "jewel"],
        "soap": ["soap", "soaps", "soaping", "soaper", "handmadesoap"],
        "candle": ["candle", "candles"],
        "textile": ["textile", "textiles"],
        "shawl": ["shawl", "shawls"],
        "utensils": ["utensils", "utensil"],
        "bag": ["bag", "bags"],
        "painting": ["painting", "paintings"],
        "earrings": ["earrings", "earring"],
        "decor": ["decor", "decoration", "decorations"],
        "beaded": ["beaded", "beading", "beads"],
        "handmade": ["handmade", "handcrafted"],
        "vegan": ["vegan", "plantbased"],
        "brass": ["brass", "brassy"],
        "beeswax": ["beeswax", "bee"],
        "handwoven": ["handwoven", "woven"],
        "terracotta": ["terracotta", "terra"],
        "wooden": ["wooden", "wood"],
        "embroidered": ["embroidered", "embroidery"]
    }
    
    # Descriptive terms from fetching scripts
    descriptive_terms = [
        "handmade", "artisan", "craft", "diy", "organic", "vegan", "natural", "traditional",
        "authentic", "rustic", "unique", "custom", "for sale", "buy", "shop", "etsy", "made",
        "create", "design"
    ]
    
    # Compute keyword diversity for normalization
    keyword_diversities = {}
    print("\nComputing Keyword Diversities:")
    print("=" * 40)
    for product, stats in product_stats.items():
        texts = stats["texts"]
        if not texts:  # Skip products with no texts
            keyword_diversities[product] = 0
            continue
        
        # Clean product name and split into tokens
        cleaned_product = re.sub(r'[^\w\s]', ' ', product.lower()).strip()
        product_tokens = cleaned_product.split()
        
        # Expand product tokens with variations
        expanded_tokens = []
        for token in product_tokens:
            if token in token_variations:
                expanded_tokens.extend(token_variations[token])
            else:
                expanded_tokens.append(token)
        
        # Product-specific keywords
        product_words = stats["all_words"]
        product_common_words = Counter(product_words).most_common(50)
        product_tokens_set = set(expanded_tokens)
        product_keywords = [word for word, count in product_common_words if word not in stop_words and word not in product_tokens_set][:3]
        keyword_diversity = len(set(word for word in product_words if word not in stop_words and word not in product_tokens_set))
        keyword_diversities[product] = keyword_diversity
        print(f"Product: {product}, Keyword Diversity: {keyword_diversity}")
    
    # Find max keyword diversity for normalization
    max_keyword_diversity = max(keyword_diversities.values()) if keyword_diversities else 1
    print(f"\nMax Keyword Diversity: {max_keyword_diversity}")
    
    for product, stats in product_stats.items():
        texts = stats["texts"]
        sentiments = stats["sentiments"]
        if not texts:  # Handle products with no texts
            analysis_data["product_stats"][product] = {
                "posts": 0,
                "comments": 0,
                "total": 0,
                "relevant": 0,
                "relevance_percentage": 0,
                "popularity_score": 0,
                "avg_sentiment": 0,
                "negative_percentage": 0,
                "keywords": []
            }
            continue
        
        # Clean product name and split into tokens
        cleaned_product = re.sub(r'[^\w\s]', ' ', product.lower()).strip()
        product_tokens = cleaned_product.split()
        
        # Expand product tokens with variations
        expanded_tokens = []
        for token in product_tokens:
            if token in token_variations:
                expanded_tokens.extend(token_variations[token])
            else:
                expanded_tokens.append(token)
        
        # Relevance: Align with fetching logic - match at least one product token OR one descriptive term
        relevant_texts = []
        # Debug: Print relevance checks for specific products
        if product in ["beaded jewelry", "handmade soap"]:
            print(f"\nDebugging Relevance for Product: {product}")
            print("=" * 40)
            print(f"Expanded Tokens: {expanded_tokens}")
            print(f"Descriptive Terms: {descriptive_terms}")
            for text in texts[:5]:  # Limit to first 5 for brevity
                text_lower = text.lower()
                # Check for product tokens
                token_matches = [token for token in expanded_tokens if any(token in word for word in text_lower.split())]
                # Check for descriptive terms
                desc_matches = [term for term in descriptive_terms if any(term in word for word in text_lower.split())]
                
                # Relevance: At least one product token OR one descriptive term
                is_relevant = len(token_matches) > 0 or len(desc_matches) > 0
                
                print(f"Text: {text}")
                print(f"Token Matches: {token_matches}")
                print(f"Descriptive Term Matches: {desc_matches}")
                print(f"Is Relevant: {is_relevant}")
                print("-" * 20)
        
        # Debug: Print texts that are not relevant
        non_relevant_texts = []
        for text in texts:
            text_lower = text.lower()
            token_matches = [token for token in expanded_tokens if any(token in word for word in text_lower.split())]
            desc_matches = [term for term in descriptive_terms if any(term in word for word in text_lower.split())]
            is_relevant = len(token_matches) > 0 or len(desc_matches) > 0
            
            if is_relevant:
                relevant_texts.append(text)
            else:
                non_relevant_texts.append(text)
        
        if non_relevant_texts and product in ["beaded jewelry", "handmade soap"]:
            print(f"\nNon-Relevant Texts for Product: {product}")
            print("=" * 40)
            for text in non_relevant_texts[:5]:
                print(f"Text: {text}")
                print("-" * 20)
        
        relevance_percentage = (len(relevant_texts) / len(texts)) * 100 if texts else 0
        
        # Sentiment analysis
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        negative_percentage = (sum(1 for s in sentiments if s < 0) / len(sentiments)) * 100 if sentiments else 0
        
        # Product-specific keywords
        product_words = stats["all_words"]
        product_common_words = Counter(product_words).most_common(50)
        product_tokens_set = set(expanded_tokens)
        product_keywords = [word for word, count in product_common_words if word not in stop_words and word not in product_tokens_set][:3]
        
        # Popularity score: Total entries * (Keyword Diversity / Max Keyword Diversity)
        total_entries = len(texts)
        keyword_diversity = keyword_diversities.get(product, 0)
        popularity_score = total_entries * (keyword_diversity / max_keyword_diversity) if max_keyword_diversity > 0 else 0
        
        analysis_data["product_stats"][product] = {
            "posts": sum(1 for entry in raw_data if entry["product"] == product and entry.get("type") == "post"),
            "comments": sum(1 for entry in raw_data if entry["product"] == product and entry.get("type") == "comment"),
            "total": len(texts),
            "relevant": len(relevant_texts),
            "relevance_percentage": relevance_percentage,
            "popularity_score": popularity_score,
            "avg_sentiment": avg_sentiment,
            "negative_percentage": negative_percentage,
            "keywords": product_keywords
        }
    
    # General keywords
    all_words = " ".join(all_texts).split()
    common_words = Counter(all_words).most_common(50)
    analysis_data["keywords"] = [word for word, count in common_words if word not in stop_words][:5]
    
    # Step 4: Save analysis
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"data_analysis_{timestamp}.json")
    with open(output_file, "w") as f:
        json.dump(analysis_data, f)
    print(f"Saved analysis to {output_file}")
    
    # Print summary
    print("\nKeyword, Sentiment, and Popularity Analysis Summary:")
    print("=" * 30)
    for product in all_products:  # Ensure all products are printed
        stats = analysis_data["product_stats"][product]
        print(f"Product: {product}")
        print(f"  Popularity Score: {stats['popularity_score']:.2f}")
        print(f"  Relevance Percentage: {stats['relevance_percentage']:.2f}%")
        print(f"  Average Sentiment: {stats['avg_sentiment']:.4f}")
        print(f"  Negative Comments (%): {stats['negative_percentage']:.2f}%")
        print(f"  Top 3 Keywords: {stats['keywords']}")
        print()
    
    print("Top General Keywords:")
    print("=" * 30)
    print(analysis_data["keywords"])

if __name__ == "__main__":
    text_processing()