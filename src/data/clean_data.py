import os
import json
import re
from collections import Counter
from datetime import datetime

def clean_text(text):
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(r'[^\w\s,.!?-]', '', text)  # Remove special characters
    text = ' '.join(text.split())  # Normalize whitespace
    return text

def is_relevant_entry(entry):
    if not entry.get("text") or not entry.get("product") or not entry.get("id"):
        return False
    
    text = entry["text"].lower()
    spam_indicators = ["check out my", "buy now", "shop at", "visit my", "click here", "for sale"]
    if any(indicator in text for indicator in spam_indicators):
        return False
    
    # Increase minimum length to 10 words (approx. 50 characters)
    if len(text.split()) < 10:
        return False
    
    off_topic_indicators = ["subreddit", "reddit", "discord", "rules", "mods", "post removed"]
    if any(indicator in text for indicator in off_topic_indicators):
        return False
    
    # Filter out generic comments
    generic_words = ["nice", "great", "cool", "awesome", "thanks", "love it", "good", "amazing", "wonderful"]
    generic_count = sum(text.count(word) for word in generic_words)
    if generic_count > 2:  # Allow up to 2 generic words
        return False
    
    return True

def clean_data():
    input_dir = "data/raw"
    raw_files = [f for f in os.listdir(input_dir) if f.startswith("raw_social_data_") and f.endswith(".json")]
    if not raw_files:
        print("Error: No raw data files found in data/raw/")
        return
    latest_file = max(raw_files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)))
    input_file = os.path.join(input_dir, latest_file)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    seen_ids = set()
    product_mapping = {
        "handmade soap": "handmade soap",
        "vegan soap": "vegan soap",
        "leather bag": "leather bag",
        "beaded jewelry": "beaded jewelry",
        "embroidered textile": "embroidered textile",
        "handmade beeswax candle": "handmade beeswax candle",
        "handmade brass jewelry": "handmade brass jewelry",
        "handmade earrings": "handmade earrings",
        "handmade painting": "handmade painting",
        "handmade terracotta decor": "handmade terracotta decor",
        "handmade wooden utensils": "handmade wooden utensils",
        "handwoven shawl": "handwoven shawl"
    }

    total_entries = len(data)
    relevant_entries = 0
    product_counts = Counter()
    product_relevant_counts = Counter()

    for entry in data:
        entry_id = entry.get("id", "")
        if entry_id in seen_ids:
            continue
        seen_ids.add(entry_id)

        product = entry.get("product", "").strip().lower()
        if product not in product_mapping:
            continue
        entry["product"] = product_mapping[product]
        product_counts[product] += 1

        text = entry.get("text", "")
        cleaned_text = clean_text(text)
        if not cleaned_text:
            continue
        entry["text"] = cleaned_text

        if not is_relevant_entry(entry):
            continue

        cleaned_data.append(entry)
        relevant_entries += 1
        product_relevant_counts[product] += 1

    overall_relevance = (relevant_entries / total_entries * 100) if total_entries > 0 else 0

    # Calculate product relevance
    product_relevance = {}
    for product in product_counts:
        relevance = (product_relevant_counts[product] / product_counts[product] * 100) if product_counts[product] > 0 else 0
        product_relevance[product] = relevance

    print(f"Total entries: {total_entries}")
    print(f"Relevant entries after cleaning: {relevant_entries}")
    print(f"Overall Relevance: {overall_relevance:.2f}%")
    print("\nIndividual Product Relevance:")
    for product, relevance in sorted(product_relevance.items()):
        print(f"{product}: {relevance:.2f}%")

    output_dir = "data/cleaned"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"cleaned_social_data_{timestamp}.json")

    # Save cleaned data with correct structure
    output_data = {
        "entries": cleaned_data,  # Use "entries" instead of "data"
        "overall_relevance": overall_relevance,
        "product_relevance": product_relevance
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"\nSaved cleaned data to {output_file}")

if __name__ == "__main__":
    clean_data()