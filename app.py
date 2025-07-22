from flask import Flask, render_template, request
import feedparser
from datetime import datetime
from dateutil import parser as date_parser
import pytz

app = Flask(__name__)

feeds = {
    "Google News - Steel Industry": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/2146842.cms",
    "Mint": "https://www.livemint.com/rss/opinion",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "PIB - Steel": "https://pib.gov.in/RssFeeds.aspx?Type=Release"
}

keywords = [
    "steel", "ministry", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy",
    "psu", "plant", "import", "policy", "rebar", "scrap", "furnace"
]

def fetch_steel_news(keyword=None, category=None, month=None):
    articles = []
    for source_name, feed_url in feeds.items():
        if category and category != source_name:
            continue

        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            published_str = entry.get("published", "") or entry.get("updated", "")

            try:
                published_dt = date_parser.parse(published_str)
                if not published_dt.tzinfo:
                    published_dt = pytz.utc.localize(published_dt)
            except Exception:
                published_dt = datetime.now(pytz.utc)

            title_lower = title.lower()
            if not any(word in title_lower for word in keywords):
                continue

            if keyword and keyword.lower() not in title_lower:
                continue

            if month:
                try:
                    if published_dt.strftime("%B") != month:
                        continue
                except:
                    pass

            articles.append({
                "title": title,
                "link": link,
                "source": source_name,
                "date": published_dt
            })

    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles

@app.route("/")
def dashboard():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")

    articles = fetch_steel_news(keyword=keyword, category=category, month=month)
    available_months = sorted({article["date"].strftime("%B") for article in articles})
    return render_template("dashboard.html",
                           articles=articles,
                           selected_keyword=keyword,
                           selected_category=category,
                           selected_month=month,
                           available_months=available_months,
                           categories=["All Sources"] + list(feeds.keys()))

if __name__ == "__main__":
    app.run(debug=True)
