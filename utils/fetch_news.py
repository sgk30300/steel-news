import feedparser
from datetime import datetime
import pandas as pd

RSS_FEEDS = {
    "Google News": "https://news.google.com/rss/search?q=steel+industry",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods/svs/steel/rssfeedstopstories.cms",
    "Mint": "https://www.livemint.com/rss/industry"
}

def fetch_steel_news(keyword="", category="", month="", source=""):
    all_news = []
    for source_name, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if "steel" not in entry.title.lower():
                continue
            pub_date = datetime(*entry.published_parsed[:6])
            if month and pub_date.strftime("%Y-%m") != month:
                continue
            if source and source != source_name:
                continue
            all_news.append({
                "title": entry.title,
                "link": entry.link,
                "source": source_name,
                "date": pub_date.strftime("%Y-%m-%d")
            })
    all_news.sort(key=lambda x: x["date"], reverse=True)
    return all_news