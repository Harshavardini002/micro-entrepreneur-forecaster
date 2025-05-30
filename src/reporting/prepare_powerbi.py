import os
import csv
from datetime import datetime
import pandas as pd

def find_latest_predictions(predictions_dir="data/predictions"):
    """Find the latest trend_predictions CSV file in the predictions directory."""
    csv_files = [f for f in os.listdir(predictions_dir) if f.endswith(".csv") and f.startswith("trend_predictions_")]
    if not csv_files:
        raise FileNotFoundError("No trend prediction CSV files found in data/predictions/")
    
    # Sort files by timestamp (latest first)
    csv_files.sort(reverse=True)
    latest_file = os.path.join(predictions_dir, csv_files[0])
    return latest_file

def prepare_powerbi_data(min_confidence_threshold=60):
    """Prepare trend prediction data for Power BI visualization."""
    # Step 1: Find the latest prediction CSV file
    try:
        input_file = find_latest_predictions()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Step 2: Load the data using pandas
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    # Step 3: Apply transformations
    # Rename columns for clarity in Power BI
    df = df.rename(columns={
        "product": "Product",
        "current_score": "CurrentScore",
        "predicted_score": "PredictedScore",
        "trend_direction": "Trend",
        "change_percentage": "ChangePercentage",
        "confidence": "Confidence",
        "avg_cost": "AverageCost",
        "approx_income": "EstimatedMonthlyIncome"
    })

    # Round numerical columns for readability
    df["CurrentScore"] = df["CurrentScore"].round(2)
    df["PredictedScore"] = df["PredictedScore"].round(2)
    df["ChangePercentage"] = df["ChangePercentage"].round(2)
    df["Confidence"] = df["Confidence"].round(0).astype(int)
    df["AverageCost"] = df["AverageCost"].round(2)
    df["EstimatedMonthlyIncome"] = df["EstimatedMonthlyIncome"].round(2)

    # Filter by minimum confidence threshold
    df = df[df["Confidence"] >= min_confidence_threshold]

    # Add a calculated column for Potential Growth (based on PredictedScore and ChangePercentage)
    df["PotentialGrowth"] = (df["PredictedScore"] * df["ChangePercentage"] / 100).round(2)

    # Sort by PredictedScore (descending)
    df = df.sort_values(by="PredictedScore", ascending=False)

    # Step 4: Save the formatted data for Power BI
    output_dir = "data/powerbi"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"powerbi_trends_latest.csv")

    df.to_csv(output_file, index=False)
    print(f"Prepared data for Power BI and saved to {output_file}")

if __name__ == "__main__":
    # Set a minimum confidence threshold (e.g., 60%) to filter out low-confidence predictions
    prepare_powerbi_data(min_confidence_threshold=60)