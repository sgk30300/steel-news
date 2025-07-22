from flask import Flask, render_template, request
import feedparser
from datetime import datetime
from dateutil import parser as dateparser
import re

app = Flask(__name__)

feeds = {
    "Google News": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/2146842.cms",
    "Mint": "https://www.livemint.com/rss/opinion",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "PIB": "https://pib.gov.in/RssFeeds.aspx?Type=Release"
}

keywords = [
    "steel", "ministry", "sail", "nmdc", "tmt",
    "iron ore", "metal", "alloy", "psu", "plant",
    "import", "policy"
]

def filter_entry(entry):
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(kw in text for kw in keywords)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def fetch_all_news():
    articles = []
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if filter_entry(entry):
                title = entry.get("title", "")
                summary = clean_html(entry.get("summary", ""))[:300] + "..."
                link = entry.get("link", "")
                published = entry.get("published", "")

                try:
                    published_parsed = dateparser.parse(published)
                    month_str = published_parsed.strftime("%B")
                    date_str = published_parsed.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    month_str = "Unknown"
                    date_str = ""

                articles.append({
                    "source": source,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": date_str,
                    "month": month_str
                })
    return sorted(articles, key=lambda x: x['published'], reverse=True)

@app.route("/")
def index():
    keyword = request.args.get("keyword", "").lower()
    category = request.args.get("category", "")
    month = request.args.get("month", "")

    articles = fetch_all_news()

    filtered = []
    for article in articles:
        if keyword and keyword not in article["title"].lower():
            continue
        if category and article["source"] != category:
            continue
        if month and article["month"] != month:
            continue
        filtered.append(article)

    categories = sorted(set(article["source"] for article in articles))
    months = sorted(set(article["month"] for article in articles if article["month"] != "Unknown"))

    return render_template("dashboard.html", articles=filtered or articles, keyword=keyword,
                           selected_category=category, selected_month=month,
                           categories=categories, months=months)

if __name__ == "__main__":
    app.run(debug=True)