from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
from urllib.parse import urlparse
import pytz

app = Flask(__name__)

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
            title = entry.title
            link = entry.link
            summary = BeautifulSoup(entry.summary, 'html.parser').text if 'summary' in entry else ''

            # Parse published date and normalize
            try:
                date_published = entry.published
                date_obj = datetime(*entry.published_parsed[:6])
            except:
                date_obj = datetime.utcnow()

            date_obj = date_obj.replace(tzinfo=None)  # Fix offset-aware issue

            # Basic steel relevance check
            if 'steel' not in title.lower():
                continue

            articles.append({
                'date': date_obj,
                'source': src,
                'title': title,
                'summary': summary,
                'link': link
            })

    # Filter logic
    if keyword:
        articles = [a for a in articles if keyword.lower() in a['title'].lower()]

    if source:
        articles = [a for a in articles if a['source'].lower() == source.lower()]

    if month:
        articles = [a for a in articles if a['date'].strftime('%Y-%m') == month]

    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles

@app.route("/")
def dashboard():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    source = request.args.get("source", "")

    news_items = fetch_steel_news(keyword=keyword, category=category, month=month, source=source)

    months = sorted(list(set(item['date'].strftime("%Y-%m") for item in news_items)), reverse=True)
    sources = sorted(set(item['source'] for item in news_items))

    return render_template("dashboard.html",
                           news=news_items,
                           keyword=keyword,
                           category=category,
                           month=month,
                           source=source,
                           months=months,
                           sources=sources,
                           now=datetime.utcnow(),
                           current_year=datetime.utcnow().year)

if __name__ == "__main__":
    app.run(debug=True)