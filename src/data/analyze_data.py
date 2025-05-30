import os
import json
from datetime import datetime
from collections import defaultdict

def analyze_data():
    # Step 1: Load the latest raw data file
    input_dir = "data/raw"
    raw_files = [f for f in os.listdir(input_dir) if f.startswith("raw_social_data_") and f.endswith(".json")]
    if not raw_files:
        print("Error: No raw data files found in data/raw/")
        return
    latest_file = max(raw_files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)))
    input_file = os.path.join(input_dir, latest_file)

    # Load data
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Step 2: Overall product mention analysis
    descriptive_terms = [
        "handmade", "artisan", "craft", "diy", "organic", "vegan", "natural", "traditional",
        "authentic", "rustic", "unique", "custom", "for sale", "buy", "shop", "etsy", "made", "create", "design"
    ]
    product_keywords = [
        "soap", "soaps",  "soapbar",
        "scarf", "scarves", "shawl", "wrap", "shawls",
        "pottery", "ceramic", "vase", "bowl", "plate", "mug", "cup",
        "basket", "baskets", "woven", "weave", "weaving", "handwoven",
        "textile", "saree", "cloth", "fabric", "print", "printed", "textiles",
        "carving", "sculpture", "wooden", "woodwork", "wood",
        "jewelry", "necklace", "bracelet", "bead", "beads", "pendant", "ring", "earring", "earrings", "jewellery", "jewel",
        "bag", "handbag", "purse", "tote", "wallet", "bags",
        "lamp", "light", "lantern", "lighting",
        "candle", "candles", "wax", "beeswax", "bee",
        "tableware", "plates", "bowls", "dishes", "dish",
        "madhubani", "mithila",
        "painting", "artwork", "art", "canvas", "sketch", "drawing", "paintings",
        "studs", "dangles", "hoop", "drop",
        "brass", "brassy",
        "vegan", "plantbased",
        "terracotta", "terra",
        "embroidered", "embroidery"
    ]

    matched_entries = 0
    unmatched_entries = []
    for entry in data:
        if not isinstance(entry.get("text", ""), str):
            continue
        text = entry["text"].lower()
        product = entry.get("product", "").strip().lower()

        # Relevance logic: Product-specific keyword OR (descriptive term AND general product keyword)
        keywords_from_product = product.split()
        has_product_keywords = any(keyword in text for keyword in keywords_from_product)
        has_descriptive_terms = any(term in text for term in descriptive_terms)
        has_general_product_keywords = any(keyword in text for keyword in product_keywords)
        is_matched = has_product_keywords or (has_descriptive_terms and has_general_product_keywords)

        if is_matched:
            matched_entries += 1
        else:
            unmatched_entries.append(entry)

    print(f"Overall Product Mention Analysis for {input_file}:")
    print("=" * 60)
    print(f"Total entries: {len(data)}")
    print(f"Entries matching relevance criteria: {matched_entries}")
    print(f"Percentage: {(matched_entries / len(data) * 100) if len(data) > 0 else 0:.2f}%")
    print("\n")

    # Step 3: Per-product distribution and relevance analysis
    all_products = [
        "beaded jewelry", "handmade earrings", "handmade painting", "handmade soap",
        "leather bag", "handmade brass jewelry", "handmade beeswax candle",
        "handwoven shawl", "handmade terracotta decor", "handmade wooden utensils",
        "embroidered textile", "vegan soap"
    ]

    product_counts = defaultdict(lambda: {"posts": 0, "comments": 0, "relevant_posts": 0, "relevant_comments": 0})

    for entry in data:
        text = entry.get("text", "").lower()
        product = entry.get("product", "").strip().lower()
        entry_id = entry.get("id", "")

        if not product or not text or not entry_id:
            continue

        # Determine if it's a post or comment
        is_comment = entry_id.startswith("comment_")
        if is_comment:
            product_counts[product]["comments"] += 1
        else:
            product_counts[product]["posts"] += 1

        # Relevance detection
        keywords_from_product = product.split()
        has_product_keywords = any(keyword in text for keyword in keywords_from_product)
        has_descriptive_terms = any(term in text for term in descriptive_terms)
        has_general_product_keywords = any(keyword in text for keyword in product_keywords)

        is_relevant = has_product_keywords or (has_descriptive_terms and has_general_product_keywords)
        if is_relevant:
            if is_comment:
                product_counts[product]["relevant_comments"] += 1
            else:
                product_counts[product]["relevant_posts"] += 1

    # Ensure all products are in product_counts
    for product in all_products:
        if product not in product_counts:
            product_counts[product] = {"posts": 0, "comments": 0, "relevant_posts": 0, "relevant_comments": 0}

    # Print results
    print("Product Distribution and Relevance:")
    print("=" * 60)
    print(f"{'Product':<25} {'Posts':<8} {'Comments':<10} {'Total':<8} {'Relevant':<10} {'Relevance %':<12}")
    print("-" * 60)

    total_posts, total_comments, total_relevant_posts, total_relevant_comments = 0, 0, 0, 0
    for product in sorted(all_products):
        counts = product_counts[product]
        total = counts["posts"] + counts["comments"]
        relevant_total = counts["relevant_posts"] + counts["relevant_comments"]
        relevance_percentage = (relevant_total / total * 100) if total > 0 else 0
        print(f"{product:<25} {counts['posts']:<8} {counts['comments']:<10} {total:<8} {relevant_total:<10} {relevance_percentage:.2f}%")
        total_posts += counts["posts"]
        total_comments += counts["comments"]
        total_relevant_posts += counts["relevant_posts"]
        total_relevant_comments += counts["relevant_comments"]

    total_all = total_posts + total_comments
    total_relevant = total_relevant_posts + total_relevant_comments
    total_relevance_percentage = (total_relevant / total_all * 100) if total_all > 0 else 0

    print("-" * 60)
    print(f"{'Total':<25} {total_posts:<8} {total_comments:<10} {total_all:<8} {total_relevant:<10} {total_relevance_percentage:.2f}%")

    # Step 4: Debug entries that are not relevant
    print("\nDebugging: Sample entries not marked as relevant (first 5):")
    print("=" * 60)
    for entry in unmatched_entries[:5]:
        print(f"Product: {entry.get('product', 'N/A')}")
        print(f"Text: {entry.get('text', '')[:100]}...")
        print("-" * 50)

    # Step 5: Save the analysis
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    analysis_data = {
        "file_analyzed": input_file,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_stats": {
            "total_posts": len(data),
            "entries_matching_relevance_criteria": matched_entries,
            "percentage_matching": (matched_entries / len(data) * 100) if len(data) > 0 else 0
        },
        "product_stats": {
            product: {
                "posts": counts["posts"],
                "comments": counts["comments"],
                "total": counts["posts"] + counts["comments"],
                "relevant": counts["relevant_posts"] + counts["relevant_comments"],
                "relevance_percentage": ((counts["relevant_posts"] + counts["relevant_comments"]) / (counts["posts"] + counts["comments"]) * 100)
                if (counts["posts"] + counts["comments"]) > 0 else 0
            }
            for product, counts in sorted(product_counts.items())
        },
        "totals": {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_count": total_all,
            "total_relevant": total_relevant,
            "overall_relevance_percentage": total_relevance_percentage
        }
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=4)
    print(f"\nSaved analysis to {output_file}")

if __name__ == "__main__":
    analyze_data()