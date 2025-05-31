import os
import csv
import json
from datetime import datetime
import sys

# ANSI color codes for console output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# Detect if the terminal supports ANSI colors (especially for PowerShell on Windows)
def supports_color():
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        try:
            os.system("")
            return True
        except:
            return False
    return True

USE_COLORS = supports_color()

def predict_trend(post_count, keyword_count, sentiment, approx_income, product_relevance):
    social_score = (post_count * 5) + (keyword_count * 0.5) + (sentiment * 100)
    income_score = approx_income * 0.1
    trend_score = (0.7 * social_score) + (0.3 * income_score)

    if trend_score > 2000:
        growth_rate = 1.05
        trend_direction = "Rising"
    elif trend_score < 500:
        growth_rate = 0.95
        trend_direction = "Declining"
    else:
        growth_rate = 1.0
        trend_direction = "Stable"

    predicted_score = trend_score * growth_rate

    # Updated confidence calculation
    base_confidence = 60  # Increased from 50 to 60
    post_factor = min(post_count / 5, 10.0)  # Reduced divisor from 10 to 5, capped at 10%
    keyword_factor = min(keyword_count / 50, 5.0)  # Reduced divisor from 100 to 50, capped at 5%
    sentiment_factor = (sentiment + 1) / 2 * 10  # Normalize sentiment (-1 to 1) to contribute up to 10%
    relevance_factor = (product_relevance / 100) * 10  # Up to 10% based on product relevance
    confidence = base_confidence + post_factor + keyword_factor + sentiment_factor + relevance_factor
    confidence = min(95, max(60, confidence))  # Clamp between 60% and 95%

    change_percentage = ((predicted_score - trend_score) / trend_score) * 100 if trend_score != 0 else 0

    return trend_score, predicted_score, trend_direction, confidence, change_percentage

def predict_trends(min_score_threshold=0):
    input_file = "data/processed/processed_trends.csv"
    if not os.path.exists(input_file):
        print("Error: Processed trends file not found.")
        return

    expected_columns = ["product", "post_count", "keyword_count", "sentiment", "individual_cost", "estimated_monthly_revenue", "estimated_yearly_revenue", "product_relevance"]
    trends_data = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not all(col in reader.fieldnames for col in expected_columns):
                missing_cols = [col for col in expected_columns if col not in reader.fieldnames]
                print(f"Error: Missing required columns in {input_file}: {missing_cols}")
                return
            
            # Debugging: Print all products being loaded
            print("\nProducts loaded from processed_trends.csv:")
            print("-" * 40)
            for row in reader:
                print(f"Product: {row['product']}")
                trends_data.append({
                    "product": row["product"],
                    "post_count": int(row["post_count"]),
                    "keyword_count": int(row["keyword_count"]),
                    "sentiment": float(row["sentiment"]),
                    "avg_cost": float(row["individual_cost"]),
                    "approx_income": float(row["estimated_monthly_revenue"]),
                    "product_relevance": float(row["product_relevance"])
                })
    except KeyError as e:
        print(f"Error: Missing expected column in {input_file}: {e}")
        return
    except ValueError as e:
        print(f"Error: Invalid data format in {input_file}: {e}")
        return

    # Debugging: Confirm total number of products loaded
    print(f"\nTotal products loaded: {len(trends_data)}")
    print("-" * 40)

    predictions = []
    for item in trends_data:
        product = item["product"]
        post_count = item["post_count"]
        keyword_count = item["keyword_count"]
        sentiment = item["sentiment"]
        avg_cost = item["avg_cost"]
        approx_income = item["approx_income"]
        product_relevance = item["product_relevance"]

        current_score, predicted_score, trend_direction, confidence, change_percentage = predict_trend(
            post_count, keyword_count, sentiment, approx_income, product_relevance
        )

        if current_score < min_score_threshold:
            print(f"Skipping {product}: Current score {current_score} below threshold {min_score_threshold}")
            continue

        predictions.append({
            "product": product,
            "current_score": current_score,
            "predicted_score": predicted_score,
            "trend_direction": trend_direction,
            "confidence": confidence,
            "change_percentage": change_percentage,
            "avg_cost": avg_cost,
            "approx_income": approx_income
        })

    if not predictions:
        print("No products meet the minimum score threshold for prediction.")
        return

    predictions.sort(key=lambda x: x["predicted_score"], reverse=True)

    # Display predictions with straight line separators between columns
    print("\nTrend Prediction Results (Next 3 Months):")
    print("=" * 89)
    
    # Define column widths (adjusted for the | separators)
    col_widths = {
        "No.": 5,
        "Product": 26,
        "Current Score": 15,
        "Predicted Score": 15,
        "Trend": 13,
        "Change": 8,  # 5 for value (e.g., -5.00) + 1 space + 2 for %
        "Confidence": 7  # 3 for value (e.g., 95) + 1 space + 2 for %
    }
    
    # Print header
    header = (
        f"{'No.':<{col_widths['No.']}} | "
        f"{'Product':<{col_widths['Product']}} | "
        f"{'Current Score':<{col_widths['Current Score']}} | "
        f"{'Predicted Score':<{col_widths['Predicted Score']}} | "
        f"{'Trend':<{col_widths['Trend']}} | "
        f"{'Change':<{col_widths['Change']}} | "
        f"{'Confidence':<{col_widths['Confidence']}}"
    )
    print(header)
    
    # Print separator with + at column boundaries
    separator = (
        "-" * col_widths["No."] + "+" +
        "-" * col_widths["Product"] + "+" +
        "-" * col_widths["Current Score"] + "+" +
        "-" * col_widths["Predicted Score"] + "+" +
        "-" * col_widths["Trend"] + "+" +
        "-" * col_widths["Change"] + "+" +
        "-" * col_widths["Confidence"]
    )
    print(separator)
    print()  # Blank line after header
    
    for idx, pred in enumerate(predictions, 1):
        trend_display = pred["trend_direction"]
        if USE_COLORS:
            if pred["trend_direction"] == "Rising":
                trend_display = f"{Colors.GREEN}{pred['trend_direction']}{Colors.RESET}"
            elif pred["trend_direction"] == "Declining":
                trend_display = f"{Colors.RED}{pred['trend_direction']}{Colors.RESET}"
            else:
                trend_display = f"{Colors.YELLOW}{pred['trend_direction']}{Colors.RESET}"
        
        # Format Change and Confidence with exact spacing
        change_str = f"{pred['change_percentage']:>5.2f} %"
        confidence_str = f"{pred['confidence']:>3.0f} %"
        
        row = (
            f"{idx:<{col_widths['No.']}} | "
            f"{pred['product']:<{col_widths['Product']}} | "
            f"{pred['current_score']:<{col_widths['Current Score']}.2f} | "
            f"{pred['predicted_score']:<{col_widths['Predicted Score']}.2f} | "
            f"{trend_display:<{col_widths['Trend']}} | "
            f"{change_str:<{col_widths['Change']}} | "
            f"{confidence_str:<{col_widths['Confidence']}}"
        )
        print(row)
        print()  # Blank line between rows

    print(separator)

    if not USE_COLORS:
        print("\nNote: Trend colors (Rising: green, Stable: yellow, Declining: red) are not displayed. To enable colors in PowerShell, run: [Console]::OutputEncoding = [System.Text.Encoding]::UTF8")

    # Save predictions to both JSON and CSV
    output_dir = "data/predictions"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_output_file = os.path.join(output_dir, f"trend_predictions_{timestamp}.json")
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=4)
    
    csv_output_file = os.path.join(output_dir, f"trend_predictions_{timestamp}.csv")
    with open(csv_output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product", "current_score", "predicted_score", "trend_direction", "change_percentage", "confidence", "avg_cost", "approx_income"])
        for pred in predictions:
            writer.writerow([
                pred["product"],
                pred["current_score"],
                pred["predicted_score"],
                pred["trend_direction"],
                pred["change_percentage"],
                pred["confidence"],
                pred["avg_cost"],
                pred["approx_income"]
            ])

    print(f"\nSaved predictions to {json_output_file} (JSON) and {csv_output_file} (CSV)")

if __name__ == "__main__":
    predict_trends(min_score_threshold=0)