# ---------------- app.py ----------------
from flask import Flask, render_template, request
import feedparser
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)

# Define RSS feeds
feeds = {
    "Google News": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/2146842.cms",
    "Mint": "https://www.livemint.com/rss/opinion"
}

# Keywords to filter
keywords = ["steel", "ministry", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy", "psu", "plant", "import", "policy"]

# Helper: filter entries
def filter_entries(entries, keyword, month_filter):
    filtered = []
    for entry in entries:
        title = entry.get("title", "").lower()
        summary = entry.get("summary", "").lower()
        published = entry.get("published", "")
        pub_date = None

        try:
            pub_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
        except:
            try:
                pub_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
            except:
                continue

        if keyword and keyword.lower() not in title and keyword.lower() not in summary:
            continue

        if month_filter:
            year, month = month_filter.split("-")
            if pub_date.year != int(year) or pub_date.month != int(month):
                continue

        filtered.append({
            "title": entry.get("title"),
            "link": entry.get("link"),
            "published": pub_date,
            "source": entry.get("source", {}).get("title", "Unknown")
        })

    return filtered

@app.route("/")
def index():
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "")
    month = request.args.get("month")

    all_news = []
    for source, url in feeds.items():
        if category and category != source:
            continue

        parsed = feedparser.parse(url)
        entries = parsed.entries
        news_items = filter_entries(entries, keyword, month)
        for item in news_items:
            item["source"] = source
        all_news.extend(news_items)

    all_news.sort(key=lambda x: x["published"], reverse=True)

    # Month dropdown (last 12 months)
    months = []
    today = datetime.today()
    for i in range(12):
        date = datetime(today.year, today.month, 1)
        month_date = date.replace(month=((date.month - i - 1) % 12 + 1),
                                  year=date.year - ((i + (12 - date.month)) // 12))
        months.append((month_date.strftime("%Y-%m"), month_date.strftime("%B %Y")))

    return render_template("dashboard.html", news=all_news, keyword=keyword,
                           category=category, selected_month=month, months=months)

if __name__ == "__main__":
    app.run(debug=True)