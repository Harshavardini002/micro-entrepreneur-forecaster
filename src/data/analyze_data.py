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
    with open(input_file, "r") as f:
        data = json.load(f)
    
    # Step 2: Overall product mention analysis
    product_keywords = [
        "soap", "soaps", "shampoo", "bar",
        "scarf", "scarves", "shawl", "wrap",
        "pottery", "ceramic", "vase", "bowl", "plate", "mug", "cup",
        "basket", "baskets", "woven", "weave",
        "textile", "shawl", "saree", "cloth", "weaving",
        "carving", "sculpture", "wooden", "woodwork",
        "jewelry", "necklace", "bracelet", "bead", "beads", "pendant", "ring",
        "bag", "handbag", "purse", "tote", "wallet",
        "lamp", "light", "lantern", "lighting",
        "fabric", "print", "printed", "textile", "cloth",
        "candle", "candles", "wax",
        "tableware", "plates", "bowls", "dishes", "dish",
        "madhubani", "mithila",
        "painting", "artwork", "art", "canvas", "sketch", "drawing",
        "earring", "earrings", "studs", "dangles", "hoop", "drop"
    ]
    
    matched_posts = 0
    unmatched_entries = []
    for post in data:
        if not isinstance(post.get("text", ""), str):
            continue
        post_lower = post["text"].lower()
        mentions_product = any(keyword in post_lower for keyword in product_keywords)
        if mentions_product:
            matched_posts += 1
        else:
            unmatched_entries.append(post)
    
    print(f"Overall Product Mention Analysis for {input_file}:")
    print("=" * 60)
    print(f"Total posts: {len(data)}")
    print(f"Posts mentioning a product: {matched_posts}")
    print(f"Percentage: {(matched_posts / len(data) * 100) if len(data) > 0 else 0:.2f}%")
    print("\n")
    
    # Step 3: Per-product distribution and relevance analysis
    descriptive_terms = [
        "handmade", "artisan", "craft", "diy", "organic", "vegan", "natural", "traditional",
        "authentic", "rustic", "unique", "custom", "for sale", "buy", "shop", "etsy", "made", "create", "design"
    ]
    
    product_counts = defaultdict(lambda: {"posts": 0, "comments": 0, "relevant_posts": 0, "relevant_comments": 0})
    for entry in data:
        if not isinstance(entry, dict) or "product" not in entry or "id" not in entry or "text" not in entry:
            continue
        product = entry["product"]
        text = entry["text"].lower()
        
        # Determine if it's a post or comment
        is_comment = entry["id"].startswith("comment_")
        if is_comment:
            product_counts[product]["comments"] += 1
        else:
            product_counts[product]["posts"] += 1
        
        # Check relevance: contains product-specific keywords OR (descriptive terms AND broad product keywords)
        product_keywords_specific = product.lower().split()
        has_product_keywords = any(keyword in text for keyword in product_keywords_specific)
        has_descriptive_terms = any(term in text for term in descriptive_terms)
        has_broad_product_keywords = any(keyword in text for keyword in product_keywords)
        is_relevant = has_product_keywords or (has_descriptive_terms and has_broad_product_keywords)
        if is_relevant:
            if is_comment:
                product_counts[product]["relevant_comments"] += 1
            else:
                product_counts[product]["relevant_posts"] += 1
    
    # Print results
    print(f"Product Distribution and Relevance for {input_file}:")
    print("=" * 60)
    print(f"{'Product':<25} {'Posts':<8} {'Comments':<10} {'Total':<8} {'Relevant':<10} {'Relevance %':<12}")
    print("-" * 60)
    total_posts, total_comments, total_relevant_posts, total_relevant_comments = 0, 0, 0, 0
    for product, counts in sorted(product_counts.items()):
        total = counts["posts"] + counts["comments"]
        relevant_total = counts["relevant_posts"] + counts["relevant_comments"]
        relevance_percentage = (relevant_total / total * 100) if total > 0 else 0
        print(f"{product:<25} {counts['posts']:<8} {counts['comments']:<10} {total:<8} {relevant_total:<10} {relevance_percentage:.2f}%")
        total_posts += counts["posts"]
        total_comments += counts["comments"]
        total_relevant_posts += counts["relevant_posts"]
        total_relevant_comments += counts["relevant_comments"]
    print("-" * 60)
    total_all = total_posts + total_comments
    total_relevant = total_relevant_posts + total_relevant_comments
    total_relevance_percentage = (total_relevant / total_all * 100) if total_all > 0 else 0
    print(f"{'Total':<25} {total_posts:<8} {total_comments:<10} {total_all:<8} {total_relevant:<10} {total_relevance_percentage:.2f}%")
    
    # Step 4: Debug entries that don't mention a product but are marked as relevant
    print("\nDebugging: Sample of entries not mentioning a product (first 5):")
    print("=" * 60)
    for entry in unmatched_entries[:5]:
        print(f"Product: {entry['product']}")
        print(f"Text: {entry['text'][:100]}...")
        print("-" * 50)
    
    # Step 5: Save the analysis for further processing
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"data_analysis_{datetime.now().strftime('%Y%m%d')}.json")
    analysis_data = {
        "file_analyzed": input_file,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_stats": {
            "total_posts": len(data),
            "posts_mentioning_products": matched_posts,
            "percentage_mentioning_products": (matched_posts / len(data) * 100) if len(data) > 0 else 0
        },
        "product_stats": {
            product: {
                "posts": counts["posts"],
                "comments": counts["comments"],
                "total": counts["posts"] + counts["comments"],
                "relevant": counts["relevant_posts"] + counts["relevant_comments"],
                "relevance_percentage": (relevant_total / total * 100) if total > 0 else 0
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
    with open(output_file, "w") as f:
        json.dump(analysis_data, f, indent=4)
    print(f"\nSaved analysis to {output_file}")

if __name__ == "__main__":
    analyze_data()