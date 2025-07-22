from flask import Flask, render_template, request
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

# --- Feed URLs ---
feeds = {
    "Google News - Steel Industry": "https://news.google.com/rss/search?q=Steel+Industry+India",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/2146842.cms",
    "Mint": "https://www.livemint.com/rss/opinion",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "PIB - Steel": "https://pib.gov.in/RssFeeds.aspx?Type=Release"
}

# --- Keywords for steel-related filtering ---
keywords = ["steel", "ministry", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy", "psu", "plant", "import", "policy"]

# --- Normalize datetime to naive ---
def normalize_datetime(dt):
    if dt is None:
        return None
    if dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt

# --- Generate month filters ---
def get_months():
    months = set()
    now = datetime.now()
    for i in range(12):
        d = datetime(now.year, now.month, 1)
        past = d.replace(month=((d.month - i - 1) % 12) + 1, year=d.year - ((i + 1) // 12))
        months.add(past.strftime("%B %Y"))
    return sorted(months, key=lambda m: datetime.strptime(m, "%B %Y"), reverse=True)

# --- Fetch and filter news ---
def fetch_news(keyword_filter=None, source_filter=None, month_filter=None):
    news_items = []
    for source, url in feeds.items():
        if source_filter and source != source_filter:
            continue
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            published = entry.get("published_parsed", None)
            if not published:
                continue
            published_date = normalize_datetime(datetime(*published[:6]))

            # Apply keyword filtering
            if not any(kw.lower() in title.lower() for kw in keywords):
                continue

            # Apply keyword search filtering
            if keyword_filter and keyword_filter.lower() not in title.lower():
                continue

            # Apply month filtering
            if month_filter and month_filter != "All Months":
                if published_date.strftime("%B %Y") != month_filter:
                    continue

            news_items.append({
                "title": title,
                "link": link,
                "published": published_date,
                "source": source
            })

    # Sort by date descending
    news_items.sort(key=lambda x: x["published"], reverse=True)
    return news_items

# --- Flask route ---
@app.route('/')
def index():
    keyword = request.args.get("keyword", "")
    source = request.args.get("source", "")
    month = request.args.get("month", "All Months")
    news = fetch_news(keyword_filter=keyword, source_filter=source or None, month_filter=month)
    return render_template("dashboard.html", news=news, months=["All Months"] + get_months(), sources=[""] + list(feeds.keys()), selected_month=month, selected_source=source, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)