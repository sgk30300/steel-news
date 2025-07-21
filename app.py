
from flask import Flask, render_template, request, send_file
import feedparser
from datetime import datetime
import pandas as pd
import hashlib
from io import BytesIO
import threading

app = Flask(__name__)

feeds = {
    "Google News - Steel Industry": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/2146842.cms",
    "Mint": "https://www.livemint.com/rss/opinion",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "PIB - Steel": "https://pib.gov.in/RssFeeds.aspx?Type=Release"
}

keywords = ["steel", "ministry", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy", "psu", "plant", "import", "policy"]

def fetch_news():
    seen = set()
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
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            if not any(keyword in title.lower() + summary.lower() for keyword in keywords):
                continue
            uid = hashlib.md5(title.encode()).hexdigest()
            if uid in seen:
                continue
            seen.add(uid)
            news_items.append({
                "Date": pub_date.strftime("%Y-%m-%d"),
                "Title": title,
                "Source": source,
                "Link": entry.link
            })
    return news_items

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").lower()
    news = fetch_news()
    if query:
        news = [item for item in news if query in item['Title'].lower()]
    return render_template("index.html", news=news, query=query)

@app.route("/export/excel")
def export_excel():
    news = fetch_news()
    df = pd.DataFrame(news)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="Steel_News.xlsx", as_attachment=True)

@app.route("/export/pdf")
def export_pdf():
    # Placeholder for future implementation
    return "PDF export is under construction."

if __name__ == "__main__":
    app.run(debug=True)
