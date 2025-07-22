from flask import Flask, render_template, request
from datetime import datetime
from dateutil import parser as date_parser
from bs4 import BeautifulSoup
from collections import OrderedDict
import feedparser
import requests

app = Flask(__name__)

def scrape_google_news(keyword="steel"):
    url = f"https://news.google.com/rss/search?q={keyword}+when:7d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        try:
            published = date_parser.parse(entry.published)
        except Exception:
            published = datetime.utcnow()
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "source": "Google News",
            "date": published,
            "summary": entry.get("summary", "")
        })
    return articles

def scrape_economic_times():
    url = "https://economictimes.indiatimes.com/industry/indl-goods/svs/steel"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    articles = []
    for item in soup.select(".eachStory"):
        title = item.find("h3")
        link = item.find("a")
        date_tag = item.find("time")
        if title and link:
            try:
                published = date_parser.parse(date_tag.text.strip()) if date_tag else datetime.utcnow()
            except Exception:
                published = datetime.utcnow()
            articles.append({
                "title": title.text.strip(),
                "link": "https://economictimes.indiatimes.com" + link.get("href", ""),
                "source": "Economic Times",
                "date": published,
                "summary": ""
            })
    return articles

def scrape_mint():
    url = "https://www.livemint.com/Search/Link/Keyword/steel"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    articles = []
    for item in soup.select("div.listView"):
        title = item.find("h2")
        link = item.find("a")
        date_tag = item.find("span", class_="date")
        if title and link:
            try:
                published = date_parser.parse(date_tag.text.strip()) if date_tag else datetime.utcnow()
            except Exception:
                published = datetime.utcnow()
            articles.append({
                "title": title.text.strip(),
                "link": "https://www.livemint.com" + link.get("href", ""),
                "source": "Mint",
                "date": published,
                "summary": ""
            })
    return articles

def fetch_steel_news(keyword="steel", category=None, month=None, source=None):
    articles = []

    if not source or source == "Google News":
        try:
            g_news = scrape_google_news(keyword)
            print(f"✅ Google News: {len(g_news)} articles")
            articles.extend(g_news)
        except Exception as e:
            print(f"❌ Google News error: {e}")

    if not source or source == "Economic Times":
        try:
            et_news = scrape_economic_times()
            print(f"✅ Economic Times: {len(et_news)} articles")
            articles.extend(et_news)
        except Exception as e:
            print(f"❌ Economic Times error: {e}")

    if not source or source == "Mint":
        try:
            mint_news = scrape_mint()
            print(f"✅ Mint: {len(mint_news)} articles")
            articles.extend(mint_news)
        except Exception as e:
            print(f"❌ Mint error: {e}")

    # Filter
    filtered = []
    for article in articles:
        if category and category.lower() not in article["title"].lower():
            continue
        if month and article["date"].strftime("%B %Y") != month:
            continue
        filtered.append(article)

    filtered.sort(key=lambda x: x["date"], reverse=True)

    # Build month list from all articles (not filtered)
    unique_months = sorted({a["date"].strftime("%B %Y") for a in articles}, reverse=True)
    return filtered, unique_months, ["Google News", "Economic Times", "Mint"]

    # Filter
    filtered = []
    for article in articles:
        if category and category.lower() not in article["title"].lower():
            continue
        if month and article["date"].strftime("%B %Y") != month:
            continue
        filtered.append(article)

    filtered.sort(key=lambda x: x["date"], reverse=True)
    unique_months = sorted(set(a["date"].strftime("%B %Y") for a in articles), reverse=True)
    return filtered, unique_months, ["Google News", "Economic Times", "Mint"]

@app.route("/")
def dashboard():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    source = request.args.get("source", "")

    news_items, months, sources = fetch_steel_news(keyword, category, month, source)

    return render_template("dashboard.html",
                           news=news_items,
                           keyword=keyword,
                           category=category,
                           selected_month=month,
                           selected_source=source,
                           months=months,
                           sources=sources,
                           current_year=datetime.utcnow().year)

if __name__ == "__main__":
    import os
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
