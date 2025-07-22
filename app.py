
from flask import Flask, render_template, request
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

# RSS Feeds
FEEDS = {
    'Google News': 'https://news.google.com/rss/search?q=steel+industry+india',
    'Economic Times': 'https://economictimes.indiatimes.com/rssfeeds/1977021501.cms',
    'Mint': 'https://www.livemint.com/rss/industry'
}

def fetch_articles():
    articles = []
    seen_links = set()
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link in seen_links:
                continue
            seen_links.add(entry.link)
            pub_date = getattr(entry, 'published', getattr(entry, 'updated', ''))
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': pub_date,
                'source': source
            })
    articles.sort(key=lambda x: x['published'], reverse=True)
    return articles

@app.route("/", methods=["GET"])
def dashboard():
    articles = fetch_articles()
    keyword = request.args.get("keyword", "").lower()
    source_filter = request.args.get("source", "")
    date_filter = request.args.get("date", "")
    if keyword:
        articles = [a for a in articles if keyword in a["title"].lower()]
    if source_filter:
        articles = [a for a in articles if a["source"] == source_filter]
    if date_filter:
        articles = [a for a in articles if date_filter in a["published"]]
    sources = list(FEEDS.keys())
    return render_template("dashboard.html", articles=articles, sources=sources)

if __name__ == "__main__":
    app.run(debug=True)
