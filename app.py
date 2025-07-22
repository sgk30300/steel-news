from flask import Flask, render_template, request
import feedparser
from datetime import datetime
import re

app = Flask(__name__)

feeds = {
    "Google News - Steel Industry": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/2146842.cms",
    "Mint": "https://www.livemint.com/rss/opinion",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "PIB - Steel": "https://pib.gov.in/RssFeeds.aspx?Type=Release"
}

keywords = ["steel", "ministry", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy", "psu", "plant", "import", "policy"]

def filter_articles(entries, keyword, month, category):
    filtered = []
    for entry in entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        published = entry.get("published", "")
        source = entry.get("source", "")
        link = entry.get("link", "")

        # Filter by keyword
        if keyword and keyword.lower() not in title.lower() + summary.lower():
            continue

        # Filter by category
        if category and category != source:
            continue

        # Filter by month
        if month:
            try:
                pub_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
            except ValueError:
                try:
                    pub_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    continue

            if pub_date.strftime("%Y-%m") != month:
                continue

        filtered.append({
            "title": title,
            "summary": summary,
            "link": link,
            "published": published,
            "source": source
        })
    return filtered

@app.route("/")
def home():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")

    articles = []
    for source, url in feeds.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            entry["source"] = source
            # Only keep entries that match keywords
            if any(kw in entry.title.lower() + entry.get("summary", "").lower() for kw in keywords):
                articles.append(entry)

    filtered = filter_articles(articles, keyword, month, category)

    # Extract available months for filter dropdown
    months = sorted({datetime.strptime(a.published, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m")
                    for a in articles if hasattr(a, "published")}, reverse=True)

    return render_template("index.html",
                           articles=filtered,
                           keyword=keyword,
                           category=category,
                           month=month,
                           months=months,
                           categories=list(feeds.keys()))

if __name__ == "__main__":
    app.run(debug=True)
