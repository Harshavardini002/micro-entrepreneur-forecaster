# src/utils/text_processing.py
import spacy
import re

def extract_keywords(posts):
    nlp = spacy.load("en_core_web_sm")
    keywords = []
    for post in posts:
        post_lower = post.lower()
        doc = nlp(post)
        product_patterns = [
            (r'handmade\s*(soap|soaps)|organic\s*soap|vegan\s*soap', "Handmade Soap"),
            (r'handmade\s*(scarf|scarves)|knitted\s*(scarf|scarves)|crochet\s*(scarf|scarves)', "Handmade Scarf"),
            (r'pottery|ceramic|ceramics', "Pottery"),
            (r'handwoven\s*(basket|baskets)|woven\s*basket', "Handwoven Basket"),
            (r'embroidered\s*(textile|shawl|saree)', "Embroidered Textile"),
            (r'wood\s*(carving|sculpture)|handcarved\s*wood', "Wood Carving"),
            (r'beaded\s*(jewelry|necklace|bracelet)|handmade\s*jewelry', "Beaded Jewelry"),
            (r'leather\s*(bag|handbag)|artisan\s*leather', "Leather Bag"),
            (r'brass\s*(lamp|light)|handmade\s*brass', "Brass Lamp"),
            (r'block\s*printed\s*(fabric|textile)|hand\s*block\s*print', "Block Printed Fabric"),
            (r'handmade\s*(candle|candles)|soy\s*candle', "Handmade Candle"),
            (r'ceramic\s*(tableware|plates|bowls)|handmade\s*tableware', "Ceramic Tableware"),
            (r'madhubani\s*(painting|art)|mithila\s*art', "Madhubani Painting"),
            (r'handmade\s*(painting|artwork)|original\s*painting -abstract', "Handmade Painting")
        ]
        for pattern, keyword in product_patterns:
            if re.search(pattern, post_lower):
                keywords.append(keyword)
        for token in doc:
            token_text = token.text.lower()
            if token.pos_ == "ADJ" and token_text in [
                'organic', 'vegan', 'natural', 'luxury', 'exfoliating', 'hydrating', 'eco-friendly',
                'beautiful', 'unique', 'vibrant', 'stunning', 'handcrafted', 'cozy', 'rustic', 'intricate',
                'elegant', 'artisan', 'traditional', 'modern', 'authentic', 'ornate', 'delicate', 'textured'
            ]:
                keywords.append(token_text)
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if any(word in chunk_text for word in ['soap', 'scarf', 'pottery', 'basket', 'textile', 'carving', 'jewelry', 'bag', 'lamp', 'fabric', 'candle', 'tableware', 'painting']):
                if (len(chunk_text.split()) <= 3 and
                    len(chunk_text) > 3 and
                    not chunk_text.startswith(('a ', 'the ', 'my ', 'this ', 'some ')) and
                    not any(bad in chunk_text for bad in [
                        'digital', 'sale', 'shop', 'etsy', 'figurine', 'duck', 'frog', 'course', 'class', 'awesome'
                    ])):
                    keywords.append(chunk.text)
    keywords = [k.title() for k in set(k.lower() for k in keywords) if k]
    blacklist = ['soap', 'scarf', 'pottery', 'basket', 'textile', 'jewelry', 'bag', 'lamp', 'fabric', 'candle', 'tableware', 'painting']
    keywords = [k for k in keywords if k.lower() not in blacklist]
    return sorted(keywords)

if __name__ == "__main__":
    sample_posts = [
        "Handmade soap, organic and vegan, smells amazing!",
        "My handmade scarf is cozy and crocheted.",
        "Pottery mug, rustic and handcrafted.",
        "Handwoven basket, intricate and natural."
    ]
    keywords = extract_keywords(sample_posts)
    print("Extracted keywords:", keywords)