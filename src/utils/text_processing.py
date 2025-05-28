import spacy
import re
from textblob import TextBlob

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    """
    Extract precise keywords using spaCy and regex, returning a list of tokens.
    """
    if not isinstance(text, str):
        return []  # Return empty list if input is not a string
    keywords = []
    text_lower = text.lower()
    doc = nlp(text)
    
    # Product patterns for specific artisan products
    product_patterns = [
        (r'handmade\s*(soap|soaps)|organic\s*soap|vegan\s*soap|soap|shampoo', "handmade soap"),
        (r'handmade\s*(scarf|scarves)|knitted\s*(scarf|scarves)|crochet\s*(scarf|scarves)|scarf|shawl', "handmade scarf"),
        (r'pottery|ceramic|ceramics|vase|bowl|plate', "pottery"),
        (r'handwoven\s*(basket|baskets)|woven\s*basket|basket|woven', "handwoven basket"),
        (r'embroidered\s*(textile|shawl|saree)|textile|cloth', "embroidered textile"),
        (r'wood\s*(carving|sculpture)|handcarved\s*wood|carving|wooden', "wood carving"),
        (r'beaded\s*(jewelry|necklace|bracelet)|handmade\s*jewelry|jewelry|necklace|bracelet|bead|beads', "beaded jewelry"),
        (r'leather\s*(bag|handbag)|artisan\s*leather|bag|handbag|purse', "leather bag"),
        (r'brass\s*(lamp|light)|handmade\s*brass|lamp|light|lantern', "brass lamp"),
        (r'block\s*printed\s*(fabric|textile)|hand\s*block\s*print|fabric|print|printed', "block printed fabric"),
        (r'handmade\s*(candle|candles)|soy\s*candle|candle|candles', "handmade candle"),
        (r'ceramic\s*(tableware|plates|bowls)|handmade\s*tableware|tableware|plates|bowls|dishes', "ceramic tableware"),
        (r'madhubani\s*(painting|art)|mithila\s*art', "madhubani painting"),
        (r'handmade\s*(painting|artwork)|original\s*painting\s*-abstract|painting|artwork|art|canvas', "handmade painting"),
        (r'handmade\s*(earring|earrings)|stud\s*earrings|dangle\s*earrings|earring|earrings|studs|dangles', "handmade earrings")
    ]
    
    # Match product patterns (prioritize the main product)
    matched_product = None
    for pattern, keyword in product_patterns:
        if re.search(pattern, text_lower):
            matched_product = keyword
            keywords.append(keyword)
            break  # Stop after the first product match to avoid duplicates
    
    # Extract descriptive terms (adjectives or relevant nouns)
    descriptive_terms = [
        'organic', 'vegan', 'natural', 'luxury', 'exfoliating', 'hydrating', 'eco-friendly',
        'beautiful', 'unique', 'vibrant', 'stunning', 'handcrafted', 'cozy', 'rustic', 'intricate',
        'elegant', 'artisan', 'traditional', 'modern', 'authentic', 'ornate', 'delicate', 'textured',
        'tarnish resistant', 'stainless steel', 'titanium', 'custom', 'smooth', 'soft', 'shiny',
        'colorful', 'lightweight', 'durable', 'scented', 'fragrant', 'herbal', 'lavender', 'chinese',
        'popular', 'basic', 'household', 'marseille', 'black', 'protective', 'frozen', 'refrigerated',
        'amazing', 'wonderful', 'gorgeous', 'lovely', 'perfect', 'excellent', 'rich', 'vibrant'
    ]
    for token in doc:
        token_text = token.text.lower()
        if token_text in descriptive_terms:
            keywords.append(token_text)
    
    # Extract noun chunks with strict constraints
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        # Skip chunks that are variations of the matched product
        if matched_product and any(word in chunk_text for word in matched_product.split()):
            continue
        if any(word in chunk_text for word in ['soap', 'scarf', 'pottery', 'basket', 'textile', 'carving', 'jewelry', 'bag', 'lamp', 'fabric', 'candle', 'tableware', 'painting', 'earring']):
            if (len(chunk_text.split()) <= 4 and
                len(chunk_text) > 3 and
                not chunk_text.startswith(('a ', 'the ', 'my ', 'this ', 'some ')) and
                not any(bad in chunk_text for bad in [
                    'digital', 'sale', 'shop', 'etsy', 'figurine', 'duck', 'frog', 'course', 'class', 'awesome'
                ])):
                keywords.append(chunk_text)
    
    # Extract entities (e.g., herbs like "cebaiye")
    for ent in doc.ents:
        ent_text = ent.text.lower()
        if ent.label_ in ["PERSON", "ORG", "PRODUCT", "GPE"] and len(ent_text.split()) <= 3:
            # Skip entities that are variations of the matched product
            if matched_product and any(word in ent_text for word in matched_product.split()):
                continue
            if ent_text not in ['i', 'we', 'you', 'they', 'it', 'this', 'that']:
                keywords.append(ent_text)
    
    # Extract adjectives (strictly from descriptive terms)
    for token in doc:
        if token.pos_ == "ADJ":
            token_text = token.text.lower()
            if token_text in descriptive_terms and token_text not in keywords:
                keywords.append(token_text)
    
    # Expanded blacklist to remove generic terms
    blacklist = [
        'soap', 'soaps', 'shampoo', 'scarf', 'scarves', 'shawl', 'pottery', 'ceramic', 'ceramics', 'vase', 'bowl', 'plate', 'basket', 'baskets', 'woven',
        'textile', 'cloth', 'saree', 'carving', 'sculpture', 'wooden', 'jewelry', 'necklace', 'bracelet', 'bead', 'beads', 'bag', 'handbag', 'purse',
        'lamp', 'light', 'lantern', 'fabric', 'print', 'printed', 'candle', 'candles', 'tableware', 'plates', 'bowls', 'dishes', 'madhubani', 'mithila',
        'painting', 'artwork', 'art', 'canvas', 'earring', 'earrings', 'studs', 'dangles',
        'also', 'always', 'here', 'just', 'many', 'more', 'most', 'once', 'only', 'perhaps', 'then', 'very', 'firstly', 'maybe', 'good',
        'different', 'little', 'social', 'cold', 'handmade', 'western', 'are', 'being', 'is', 'was', 'were', 'be', 'have', 'has', 'had',
        'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'might', 'must', 'shall', 'i', 'we', 'you', 'he', 'she', 'it',
        'they', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which', 'who', 'whom',
        'whose', 'when', 'where', 'why', 'how', 'not', 'no', 'yes', 'so', 'but', 'and', 'or', 'if', 'because', 'while', 'after', 'before',
        'since', 'until', 'though', 'although', 'even', 'as', 'like', 'with', 'without', 'in', 'on', 'at', 'to', 'for', 'from', 'by',
        'about', 'into', 'over', 'under', 'above', 'below', 'between', 'among', 'through', 'during', 'within', 'against', 'across', 'things'
    ]
    # Remove duplicates, apply blacklist, and limit to 5 keywords
    keywords = sorted(list(set(k for k in keywords if k and k not in blacklist and len(k) > 2)))
    # Prioritize: product first, then descriptive terms, then entities/noun chunks
    final_keywords = []
    # Add the product keyword first
    if matched_product:
        final_keywords.append(matched_product)
    # Add descriptive terms
    for kw in keywords:
        if kw in descriptive_terms and len(final_keywords) < 5:
            final_keywords.append(kw)
    # Add entities and noun chunks if space remains
    for kw in keywords:
        if kw not in final_keywords and kw not in descriptive_terms and len(final_keywords) < 5:
            final_keywords.append(kw)
    
    return final_keywords

def get_sentiment(text):
    """
    Compute sentiment polarity (-1 to 1) using TextBlob.
    """
    if not isinstance(text, str):
        return 0.0  # Return neutral sentiment if input is not a string
    return TextBlob(text).sentiment.polarity

if __name__ == "__main__":
    sample_text = "Hi, handmade soap is becoming a popular thing in chinese social media Hi everyone, i'm a beginner of handmade soap and i'm from china. I read some books from Taiwan teaching how to make basic soaps like Household soap and Marseille soap and more. Now, in little red book(one of the most popular social media in china), there are not only basic handmade soaps but also many with chinese traditional herbs. I read the recipes and most of the herbs are crushed into powder and then drop very little of them(lower than 10g in a 1000g mixture) into the oil.\n\nHere are the questions, most of the function materials in chinese herbs always release after hours boiling, so i wonder could we boil them for hours firstly(maybe like boiling lavender in western for 3 or 5 hours), and then add the cooking liquor into the cold process soap?\n\nAnother one is, \"cebaiye(one of the herbs) handmade soap for hair\" now is very popular in red book! As is known that handmade soap with lye couldn't be used on hair. Here is an alternative i read: boil the herbs all together(perhaps 10 different kinds of chinese traditional herbs used to protect hair, make it black, smooth and more), and then filtration with gauze, collect the soup liquor, and pour into bottle then freeze or refrigerate it. Once wash hair, just use perhaps 8ml of the liquor. I think it's a good idea!"
    keywords = preprocess_text(sample_text)
    sentiment = get_sentiment(sample_text)
    print(f"Keywords: {keywords}")
    print(f"Sentiment: {sentiment}")