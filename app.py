
from flask import Flask, render_template
import feedparser
from datetime import datetime

app = Flask(__name__)

feeds = {
    "Google News - Ministry of Steel": "https://news.google.com/rss/search?q=Ministry+of+Steel+India",
    "Google News - Steel Industry": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Google News - SAIL": "https://news.google.com/rss/search?q=SAIL+Steel",
    "Google News - NMDC": "https://news.google.com/rss/search?q=NMDC+Steel",
    "PIB - Steel": "https://pib.gov.in/RssFeeds.aspx?Type=Release"
}

keywords = ["steel", "ministry of steel", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy", "psu", "plant", "output"]

def fetch_news(feeds, keywords):
    news_items = []
    now = datetime.now()
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            try:
                pub_date = datetime(*entry.published_parsed[:6])
            except:
                continue
            if pub_date.month != now.month or pub_date.year != now.year:
                continue
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            if any(keyword in title or summary for keyword in keywords):
                news_items.append({
                    "Date": pub_date.strftime("%Y-%m-%d"),
                    "Title": entry.title,
                    "Source": source,
                    "Link": entry.link
                })
    return news_items

@app.route("/")
def index():
    news = fetch_news(feeds, keywords)
    return render_template("index.html", news=news)

if __name__ == "__main__":
    app.run(debug=True)
