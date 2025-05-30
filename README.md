Micro-Entrepreneur Forecaster
Overview
This project helps tiny businesses (like people who make handmade things) see which products are popular! We look at Reddit posts and comments to find trends for 12 products, like vegan soap and handmade earrings. Then, we show the trends in a Power BI report with cool pictures like bar charts and pie charts. You can update the data anytime to see the latest trends!
Features

Collects Data: Gets posts and comments from Reddit about 12 artisan products.
Analyzes Trends: Finds important words (keywords) and feelings (sentiment) in the posts.
Predicts Trends: Scores products to see which ones are getting popular (like vegan soap with a score of 2761.28!).
Shows Trends in Power BI: Makes a report with:
Bar chart (top products by score).
Pie chart (trend types: Rising, Stable, Declining).
Table (details for all products).
Card (average confidence: 77.7%).
Slicer (pick a product to filter the pictures).


Manual Updates: You can update the data anytime with one click!

Project Structure
Here’s what’s in the project folder:

src/: All the Python code to collect and analyze data.
src/data/fetch_data.py: Gets Reddit posts and comments for all products.
src/data/process_trends.py: Finds keywords and feelings in the posts.
src/analysis/predict_trends.py: Scores products to predict trends.
src/reporting/prepare_powerbi.py: Makes a file (powerbi_trends_latest.csv) for Power BI.


data/: Where the data lives.
data/raw/: Raw Reddit data (e.g., raw_social_data_20250528.json).
data/processed/: Processed data (e.g., processed_trends.csv).
data/predictions/: Trend predictions (e.g., trend_predictions_20250530_233400.csv).
data/powerbi/: Data for Power BI (e.g., powerbi_trends_latest.csv).
data/cache/: Cache files to make things faster.


micro_entrepreneur_forecast.pbix: The Power BI report with all the pictures.
update_trends.bat: A file to update the data with one click.

How to Run the Project

Set Up Your Computer:
Make sure you have Python installed.
Activate the virtual environment:cd C:\Users\harsh\OneDrive\Desktop\documents\micro-entrepreneur-forecaster
.\venv\Scripts\activate


Install the required tools:pip install -r requirements.txt


Make sure you have Power BI Desktop installed.


Update the Data:
Double-click update_trends.bat in the project folder to update the data.
This runs predict_trends.py and prepare_powerbi.py to make a new powerbi_trends_latest.csv.


See the Report in Power BI Desktop:
Open micro_entrepreneur_forecast.pbix in Power BI Desktop.
Click Home > Refresh to load the new data.
Look at the pictures (bar chart, pie chart, etc.)!


See the Report Online:
The report is published to Power BI Service in My Workspace.
Go to app.powerbi.com, sign in, and look in My Workspace for micro_entrepreneur_forecast.
To update the online report, re-publish from Power BI Desktop after running update_trends.bat.



Tools Used

Python: To collect and analyze data.
PRAW: To get Reddit posts and comments.
Power BI: To make the report with pretty pictures.
Git: To save my work.

Stages of Development
I built this project in 5 stages:

Setup (Before May 28): Made the project folder, set up Python, and started Git.
Data Collection (May 28): Got ~1500 Reddit posts/comments for 12 products with 80–90% relevance.
Keyword Extraction and Sentiment Analysis (May 28): Found important words and feelings for each product.
Trend Prediction (May 29–30): Made a script to score products and predict trends.
Visualization/Reporting (May 30): Made a Power BI report and set up manual updates with update_trends.bat.

Project Status
The project is complete! I finished it at 11:36 PM IST on May 30, 2025. You can see the latest trends for tiny businesses in the Power BI report, and update the data anytime for your presentation.
