from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from dateutil import parser as date_parser
import pytz

app = Flask(__name__)

def fetch_google_news():
    url = "https://news.google.com/search?q=steel&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    articles = []

    for item in soup.select("article"):
        headline_tag = item.find("h3") or item.find("h4")
        if headline_tag:
            title = headline_tag.get_text(strip=True)
            link_tag = headline_tag.find("a")
            if link_tag and link_tag.get("href"):
                url = link_tag["href"]
                if url.startswith("."):
                    url = "https://news.google.com" + url[1:]
                if "steel" in title.lower():
                    articles.append({
                        "title": title,
                        "link": url,
                        "source": "Google News",
                        "category": "General",
                        "date": datetime.now(pytz.utc)
                    })
    return articles

def fetch_mint_news():
    url = "https://www.livemint.com/Search/Link/Keyword/steel"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    articles = []

    for item in soup.select(".listingPage .listing h2"):
        title = item.get_text(strip=True)
        link_tag = item.find("a")
        if link_tag and link_tag["href"]:
            url = link_tag["href"]
            if not url.startswith("http"):
                url = "https://www.livemint.com" + url
            if "steel" in title.lower():
                articles.append({
                    "title": title,
                    "link": url,
                    "source": "Mint",
                    "category": "Business",
                    "date": datetime.now(pytz.utc)
                })
    return articles

def fetch_steel_news(keyword=None, category=None, month=None, source=None):
    articles = []
    if not source or source == "Google News":
        articles.extend(fetch_google_news())
    if not source or source == "Mint":
        articles.extend(fetch_mint_news())

    # Filtering
    if keyword:
        articles = [a for a in articles if keyword.lower() in a['title'].lower()]
    if category:
        articles = [a for a in articles if a['category'].lower() == category.lower()]
    if month:
        articles = [a for a in articles if a['date'].strftime("%B") == month]

    # Sorting (fixing offset-naive and aware datetime comparison)
    for a in articles:
        if a['date'].tzinfo is None:
            a['date'] = pytz.utc.localize(a['date'])

    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles

@app.route("/", methods=["GET"])
def dashboard():
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    source = request.args.get("source", "")

    news_items = fetch_steel_news(keyword=keyword, category=category, month=month, source=source)

    categories = ["General", "Business"]
    months = [datetime(2025, m, 1).strftime("%B") for m in range(1, 13)]
    sources = ["Google News", "Mint"]

    return render_template("dashboard.html",
                           news=news_items,
                           keyword=keyword,
                           category=category,
                           month=month,
                           source=source,
                           categories=categories,
                           months=months,
                           sources=sources,
                           current_year=datetime.now().year)

if __name__ == "__main__":
    app.run(debug=True, port=10000)