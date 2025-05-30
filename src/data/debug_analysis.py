import os
import json

def debug_analysis():
    # Find the latest analysis file
    input_dir = "data/processed"
    analysis_files = [f for f in os.listdir(input_dir) if f.startswith("data_analysis_") and f.endswith(".json")]
    if not analysis_files:
        print("Error: No analysis files found in data/processed/")
        return
    latest_file = max(analysis_files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)))
    input_file = os.path.join(input_dir, latest_file)
    
    # Load data
    with open(input_file, "r") as f:
        analysis_data = json.load(f)
    
    # Print relevance_percentage for each product
    print(f"Contents of {input_file}:")
    print("Product | Relevance_Percentage")
    print("-" * 30)
    for product, stats in analysis_data["product_stats"].items():
        print(f"{product} | {stats['relevance_percentage']:.2f}%")

if __name__ == "__main__":
    debug_analysis()