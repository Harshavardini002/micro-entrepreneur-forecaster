# src/frontend/app.py
import streamlit as st
from data.process_trends import generate_trend_report

st.title("Artisan Market Trend Forecaster")
st.markdown("Enter artisan products to analyze trends from Reddit posts.")

products_input = st.text_area("Enter products (one per line)", "Abstract painting\nhandmade scarf\npottery")
max_posts = st.slider("Max posts per product", 1, 20, 10)

if st.button("Generate Trend Report"):
    products = [p.strip() for p in products_input.split("\n") if p.strip()]
    if products:
        with st.spinner("Fetching and processing trends..."):
            report = generate_trend_report(products, max_posts=max_posts)
        st.success("Trend report generated!")
        
        for product, keywords in report.items():
            st.subheader(f"Trends for {product}")
            if keywords:
                st.write(", ".join(keywords))
            else:
                st.write("No trends found.")
    else:
        st.error("Please enter at least one product.")

if __name__ == "__main__":
    st.write("Run with: streamlit run src/frontend/app.py")