import os
import csv
import json
from datetime import datetime

def predict_trends():
    input_file = "data/processed/processed_trends.csv"
    if not os.path.exists(input_file):
        print("Error: Processed trends file not found.")
        return

    trends_data = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trends_data.append({
                "product": row["product"],
                "post_count": int(row["post_count"]),
                "keyword_count": int(row["keyword_count"]),
                "sentiment": float(row["sentiment"]),
                "avg_cost": float(row["avg_cost"]),
                "approx_income": float(row["approx_income"])
            })

    predictions = []
    for item in trends_data:
        product = item["product"]
        post_count = item["post_count"]
        keyword_count = item["keyword_count"]
        sentiment = item["sentiment"]
        avg_cost = item["avg_cost"]
        approx_income = item["approx_income"]

        # Updated trend score formula: Include social engagement and income potential
        # Social Engagement Score: (post_count * 5) + (keyword_count * 0.5) + (sentiment * 100)
        # Income Potential: (approx_income * 0.1)
        # Total Trend Score: 0.7 * Social Engagement + 0.3 * Income Potential
        social_score = (post_count * 5) + (keyword_count * 0.5) + (sentiment * 100)
        income_score = approx_income * 0.1
        trend_score = (0.7 * social_score) + (0.3 * income_score)

        growth_rate = 1.05 if trend_score > 2000 else 1.0
        predicted_score = trend_score * growth_rate

        predictions.append({
            "product": product,
            "current_score": trend_score,
            "predicted_score": predicted_score
        })

    output_dir = "data/predictions"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"trend_predictions_{timestamp}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=4)

    print("Trend Prediction Results:")
    print("============================================================")
    print(f"{'Product':<25} {'Current Score':<15} {'Predicted Score (3 Months)':<25}")
    print("------------------------------------------------------------")
    for pred in sorted(predictions, key=lambda x: x["current_score"], reverse=True):
        print(f"{pred['product']:<25} {pred['current_score']:<15.2f} {pred['predicted_score']:<25.2f}")

    print(f"\nSaved predictions to {output_file}")

if __name__ == "__main__":
    predict_trends()