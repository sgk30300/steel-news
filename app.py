from flask import Flask, render_template, request
import feedparser
import pandas as pd
from datetime import datetime
from collections import defaultdict
import re

app = Flask(__name__)

RSS_FEEDS = {
    "Google News": "https://news.google.com/rss/search?q=steel+industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods-svs/steel/rssfeeds/13353106.cms",
    "Mint": "https://www.livemint.com/rss/industry"
}

def summarize(text, word_limit=25):
    text = re.sub(r'<[^>]+>', '', text)  # remove HTML tags
    words = text.split()
    return " ".join(words[:word_limit]) + ("..." if len(words) > word_limit else "")

def fetch_articles():
    articles = []
    seen_links = set()
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if "steel" not in entry.title.lower() and "steel" not in entry.get("summary", "").lower():
                continue
            if entry.link in seen_links:
                continue
            seen_links.add(entry.link)
            published = entry.get("published", "")
            try:
                published_dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                published_dt = datetime.utcnow()
            articles.append({
                "title": entry.title,
                "summary": summarize(entry.get("summary", "")),
                "link": entry.link,
                "published": published_dt,
                "source": source
            })
    articles.sort(key=lambda x: x["published"], reverse=True)
    return articles

@app.route("/")
def dashboard():
    articles = fetch_articles()
    keyword = request.args.get("keyword", "").lower()
    source_filter = request.args.get("source", "")
    month_filter = request.args.get("month", "")
    category_filter = request.args.get("category", "").lower()

    # Apply filters
    if keyword:
        articles = [a for a in articles if keyword in a["title"].lower() or keyword in a["summary"].lower()]
    if source_filter:
        articles = [a for a in articles if a["source"] == source_filter]
    if month_filter:
        articles = [a for a in articles if a["published"].strftime("%Y-%m") == month_filter]
    if category_filter:
        articles = [a for a in articles if category_filter in a["title"].lower() or category_filter in a["summary"].lower()]

    # Get list of months and sources for filters
    months = sorted({a["published"].strftime("%Y-%m") for a in articles}, reverse=True)
    sources = sorted({a["source"] for a in articles})
    return render_template("dashboard.html", articles=articles, sources=sources, months=months)

if __name__ == "__main__":
    app.run(debug=True)