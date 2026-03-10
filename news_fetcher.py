import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import re

def fetch_news(ticker: str, company_name: str) -> dict:
    """
    Fetch news from Google News, Yahoo Finance, and Economic Times RSS.
    Returns a unified dict with headlines, summary, and sentiment keywords.
    """
    results = {
        "ticker": ticker,
        "headlines": [],
        "sources": [],
        "sentiment_keywords": {"positive": [], "negative": []},
        "news_summary": "",
        "fetched_at": datetime.now().isoformat()
    }
    
    # Define sentiment keywords
    POS_KEYWORDS = ["growth", "profit", "beat", "surge", "gain", "deal", "order", "expansion", "bullish", "upgrade", "buy"]
    NEG_KEYWORDS = ["loss", "fall", "drop", "plunge", "concern", "miss", "penalty", "debt", "bearish", "downgrade", "sell"]

    # 1. Google News RSS
    try:
        query = f"{company_name} NSE stock"
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.text)
            for item in root.findall('.//item')[:3]:
                title = item.find('title').text
                results["headlines"].append(title)
                results["sources"].append("Google News")
    except Exception as e:
        print(f"⚠ Google News fetch failed for {ticker}: {e}")

    # 2. Yahoo Finance Search (Internal API)
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}&newsCount=5"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for news in data.get("news", [])[:3]:
                title = news.get("title")
                if title:
                    results["headlines"].append(title)
                    results["sources"].append(news.get("publisher", "Yahoo Finance"))
    except Exception as e:
        print(f"⚠ Yahoo Finance fetch failed for {ticker}: {e}")

    # 3. Economic Times RSS
    try:
        url = "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.text)
            for item in root.findall('.//item'):
                title = item.find('title').text
                # Filter ET news for relevance to company or ticker
                if ticker.split('.')[0].lower() in title.lower() or company_name.lower() in title.lower():
                    results["headlines"].append(title)
                    results["sources"].append("Economic Times")
                    if len(results["headlines"]) >= 7: break
    except Exception as e:
        print(f"⚠ Economic Times fetch failed: {e}")

    # Deduplicate and limit to 7
    seen = set()
    cleaned_headlines = []
    for h in results["headlines"]:
        if h.lower() not in seen:
            cleaned_headlines.append(h)
            seen.add(h.lower())
    results["headlines"] = cleaned_headlines[:7]
    results["sources"] = list(set(results["sources"]))

    # Extraction of keywords and summary
    all_text = " ".join(results["headlines"]).lower()
    results["sentiment_keywords"]["positive"] = list(set([w for w in POS_KEYWORDS if w in all_text]))
    results["sentiment_keywords"]["negative"] = list(set([w for w in NEG_KEYWORDS if w in all_text]))
    
    if results["headlines"]:
        results["news_summary"] = ". ".join(results["headlines"][:3])
    else:
        results["news_summary"] = "No recent news found for this ticker."

    return results

if __name__ == "__main__":
    # Test
    print(json.dumps(fetch_news("RELIANCE.NS", "Reliance Industries"), indent=2))
