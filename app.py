from flask import Flask, render_template, request
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
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

keywords = ["steel", "ministry", "sail", "nmdc", "tmt", "iron ore", "metal", "alloy", "psu", "plant", "import", "policy"]


def clean_html(html):
    return BeautifulSoup(html, "html.parser").get_text()


def make_naive(dt):
    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def fetch_news(source_filter=None, keyword_filter=None, month_filter=None):
    all_items = []
    now = datetime.now()

    for source_name, url in feeds.items():
        if source_filter and source_filter != source_name:
            continue

        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = clean_html(entry.get("summary", ""))
            link = entry.get("link", "")
            published_raw = entry.get("published", entry.get("updated", now.isoformat()))

            try:
                published = date_parser.parse(published_raw)
            except Exception:
                published = now

            if month_filter:
                if published.year != month_filter.year or published.month != month_filter.month:
                    continue

            if keyword_filter:
                keyword_match = any(kw.lower() in (title + summary).lower() for kw in keyword_filter)
                if not keyword_match:
                    continue

            all_items.append({
                "title": title,
                "summary": summary,
                "link": link,
                "source": source_name,
                "published": published
            })

    all_items.sort(key=lambda x: make_naive(x["published"]), reverse=True)
    return all_items


def get_month_list():
    now = datetime.now()
    months = []
    for i in range(12):
        month = (now.month - i - 1) % 12 + 1
        year = now.year if now.month - i > 0 else now.year - 1
        label = f"{datetime(year, month, 1).strftime('%B %Y')}"
        value = f"{year}-{month:02}"
        months.append({"label": label, "value": value})
    return months


@app.route("/")
def index():
    selected_source = request.args.get("source")
    selected_month = request.args.get("month")

    month_dt = None
    if selected_month:
        try:
            month_dt = datetime.strptime(selected_month, "%Y-%m")
        except ValueError:
            month_dt = None

    news_items = fetch_news(
        source_filter=selected_source,
        keyword_filter=keywords,
        month_filter=month_dt
    )

    months = get_month_list()
    sources = list(feeds.keys())

    return render_template("dashboard.html",
                           news=news_items,
                           selected_source=selected_source,
                           selected_month=selected_month,
                           months=months,
                           sources=sources)


if __name__ == "__main__":
    app.run(debug=True)