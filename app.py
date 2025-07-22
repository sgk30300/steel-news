from flask import Flask, render_template, request
import feedparser
from datetime import datetime, timedelta

app = Flask(__name__)

# Enhanced keyword list
steel_keywords = [
    "steel", "tmt", "iron ore", "sponge iron", "steel plant", "rolling mill",
    "steel production", "scrap metal", "smelter", "blast furnace", "nmdc",
    "sail", "jsw", "jindal", "essar steel", "arcelor mittal", "rebar", "billets",
    "ingots", "cold rolled", "hot rolled", "flat steel", "long steel",
    "alloy steel", "metal prices", "ferrous", "non-ferrous", "steel imports",
    "steel exports", "steel demand", "steel policy", "metal industry"
]

# Feeds from reliable sources
feeds = {
    "Google News": "https://news.google.com/rss/search?q=steel+OR+iron+ore+OR+tmt+OR+metal+OR+sail+OR+nmdc&hl=en-IN&gl=IN&ceid=IN:en",
    "Economic Times": "https://economictimes.indiatimes.com/industry/indl-goods/svs/steel/rssfeeds/13376306.cms",
    "Mint": "https://www.livemint.com/rss/industry"
}

def is_relevant(title, summary, keywords, threshold=1):
    text = (title + " " + summary).lower()
    return sum(kw in text for kw in keywords) >= threshold

def get_filtered_entries():
    entries = []
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                published_dt = datetime(*entry.published_parsed[:6])
                title = entry.title
                summary = entry.get('summary', '')

                # ✅ Apply keyword filtering only to Google News
                if source == "Google News":
                    if not is_relevant(title, summary, steel_keywords):
                        continue

                entries.append({
                    'title': title,
                    'link': entry.link,
                    'summary': summary,
                    'date': published_dt,
                    'source': source
                })

    return sorted(entries, key=lambda x: x['date'], reverse=True)

def get_last_3_months():
    now = datetime.now()
    months = []
    for i in range(3):
        date = now - timedelta(days=i * 30)
        months.append(date.strftime('%B %Y'))
    return list(dict.fromkeys(months))

@app.route("/", methods=["GET"])
def index():
    keyword = request.args.get("keyword", "").lower()
    source = request.args.get("category", "")
    month = request.args.get("month", "")

    news = get_filtered_entries()

    if month and month != "All Months":
        news = [n for n in news if n['date'].strftime('%B %Y') == month]

    if source:
        news = [n for n in news if n['source'] == source]

    if keyword:
        news = [n for n in news if keyword in n['title'].lower() or keyword in n['summary'].lower()]

    return render_template(
        "dashboard.html",
        news=news,
        months=["All Months"] + get_last_3_months(),
        sources=[""] + list(feeds.keys()),
        selected_month=month,
        selected_source=source,
        keyword=keyword
    )

if __name__ == "__main__":
    app.run(debug=True)
