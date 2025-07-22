from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

# RSS Feeds to fetch from
RSS_FEEDS = {
    'Google News': 'https://news.google.com/rss/search?q=steel&hl=en-IN&gl=IN&ceid=IN:en',
    'Economic Times': 'https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods-/-svs/steel/rssfeeds/13376752.cms',
    'Mint': 'https://www.livemint.com/rss/companies',
    'GMK Center': 'https://gmk.center/en/feed/'
}

def fetch_steel_news(keyword="", category="", month="", source=""):
    articles = []

    for src, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary_html = entry.get('summary', '')
            published = entry.get('published', '')

            try:
                date_obj = datetime.strptime(published.replace(' GMT', '').strip(), "%a, %d %b %Y %H:%M:%S")
            except Exception:
                try:
                    date_obj = datetime.strptime(published.strip(), "%a, %d %b %Y %H:%M:%S %z")
                except:
                    date_obj = datetime.now()

            summary = BeautifulSoup(summary_html, "html.parser").text.strip()

            if "steel" not in title.lower() and "steel" not in summary.lower():
                continue

            articles.append({
                "title": title,
                "summary": summary,
                "link": link,
                "source": src,
                "date": date_obj
            })

    # Sort by date
    articles.sort(key=lambda x: x["date"], reverse=True)

    # Filters
    if keyword:
        articles = [a for a in articles if keyword.lower() in a["title"].lower()]
    if source:
        articles = [a for a in articles if source == a["source"]]
    if month:
        articles = [a for a in articles if a["date"].strftime("%Y-%m") == month]

    return articles

@app.route("/")
def dashboard():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    source = request.args.get("source", "")

    news_items = fetch_steel_news(keyword=keyword, category=category, month=month, source=source)

    # Build list of available months and sources for dropdowns
    months = sorted(list(set(item['date'].strftime("%Y-%m") for item in news_items)), reverse=True)
    sources = sorted(set(item['source'] for item in news_items))

    return render_template("dashboard.html",
                           news=news_items,
                           keyword=keyword,
                           category=category,
                           month=month,
                           source=source,
                           months=months,
                           sources=sources)
