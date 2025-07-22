from flask import Flask, render_template, request
import feedparser
from datetime import datetime
from transformers import pipeline
import re

app = Flask(__name__)

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

RSS_FEEDS = {
    "Google News": "https://news.google.com/rss/search?q=steel+industry+when:7d&hl=en-IN&gl=IN&ceid=IN:en",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods-svs/steel/rssfeeds/13352306.cms",
    "Mint": "https://www.livemint.com/rss/companies",
    "GMK Center": "https://gmk.center/en/feed/"
}

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def summarize_text(text):
    try:
        summary = summarizer(text, max_length=40, min_length=20, do_sample=False)[0]['summary_text']
        return summary.strip()
    except Exception:
        return ""

@app.route("/", methods=["GET"])
def dashboard():
    selected_source = request.args.get("source", "All")
    selected_month = request.args.get("month", "All")
    selected_category = request.args.get("category", "All")

    all_articles = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if "steel" not in entry.title.lower():
                continue
            published = datetime(*entry.published_parsed[:6])
            if selected_month != "All" and published.strftime("%B %Y") != selected_month:
                continue
            if selected_source != "All" and selected_source != source:
                continue
            title = entry.title
            link = entry.link
            description = clean_html(entry.get("summary", ""))
            if title.strip() == description.strip():
                summary = summarize_text(title)
            else:
                summary = summarize_text(description)
            all_articles.append({
                "date": published.strftime("%Y-%m-%d"),
                "title": title,
                "summary": summary,
                "link": link,
                "source": source,
                "category": "Steel News"
            })

    all_articles.sort(key=lambda x: x["date"], reverse=True)

    sources = list(RSS_FEEDS.keys())
    months = sorted({datetime.strptime(a["date"], "%Y-%m-%d").strftime("%B %Y") for a in all_articles}, reverse=True)
    categories = sorted({a["category"] for a in all_articles})

    return render_template("dashboard.html", articles=all_articles, sources=sources, months=months, categories=categories)
