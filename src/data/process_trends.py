# src/data/process_trends.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data.fetch_data import fetch_x_posts
from utils.text_processing import extract_keywords

def generate_trend_report(products, max_posts=20):
    trend_report = {}
    all_posts = set()
    for product in products:
        posts, comments = fetch_x_posts(product, max_posts=max_posts, existing_posts=all_posts)
        keywords = extract_keywords(posts + comments)
        trend_report[product] = {"keywords": keywords, "comments": comments}
    return trend_report

if __name__ == "__main__":
    test_products = [
        "handmade soap", "handmade scarf", "pottery", "handwoven basket", "embroidered textile",
        "wood carving", "beaded jewelry", "leather bag", "brass lamp", "block printed fabric",
        "handmade candle", "ceramic tableware", "madhubani painting", "handmade painting"
    ]
    report = generate_trend_report(test_products, max_posts=20)
    for product, info in report.items():
        print(f"Trends for {product}: {info['keywords']}")