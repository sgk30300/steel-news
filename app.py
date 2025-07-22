from flask import Flask, render_template, request
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

# Define RSS feeds from reliable sources
RSS_FEEDS = {
    "Google News - Steel": "https://news.google.com/rss/search?q=steel+ministry&hl=en-IN&gl=IN&ceid=IN:en",
    "The Economic Times - Steel": "https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods/svs/steel/rssfeedstopstories.cms",
    "Mint - Industry": "https://www.livemint.com/rss/companies/industry",
}

# Function to parse and format news
def fetch_news():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            try:
                published = entry.get("published_parsed")
                if not published:
                    continue
                published_dt = datetime(*published[:6])
                published_dt = pytz.utc.localize(published_dt)
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_dt,
                    "source": source
                })
            except Exception as e:
                continue
    articles.sort(key=lambda x: x["published"], reverse=True)
    return articles

@app.route("/")
def dashboard():
    date_filter = request.args.get("date")
    source_filter = request.args.get("source")
    articles = fetch_news()

    if date_filter:
        try:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            articles = [a for a in articles if a["published"].date() == target_date]
        except:
            pass

    if source_filter:
        articles = [a for a in articles if a["source"] == source_filter]

    sources = list(RSS_FEEDS.keys())
    return render_template("dashboard.html", articles=articles, sources=sources)

if __name__ == "__main__":
    app.run(debug=True)