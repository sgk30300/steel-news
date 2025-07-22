
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import feedparser
import pandas as pd
import requests
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

RSS_FEEDS = {
    'Google News': 'https://news.google.com/rss/search?q=steel&hl=en-IN&gl=IN&ceid=IN:en',
    'Economic Times': 'https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods-/-svs/steel/rssfeeds/13376752.cms',
    'Mint': 'https://www.livemint.com/rss/companies',
    'GMK Center': 'https://gmk.center/en/feed/'
}

def fetch_news():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            date_published = entry.published if 'published' in entry else datetime.now().strftime('%a, %d %b %Y %H:%M:%S')
            date_clean = date_published.split(' GMT')[0].split(' +')[0].strip()
            date_obj = datetime.strptime(date_clean, '%a, %d %b %Y %H:%M:%S')
            summary = BeautifulSoup(entry.summary, 'html.parser').text if 'summary' in entry else ''
            if 'steel' not in title.lower():
                continue
            articles.append({
                'date': date_obj,
                'source': source,
                'title': title,
                'summary': summary,
                'link': link
            })
    return sorted(articles, key=lambda x: x['date'], reverse=True)

@app.route('/', methods=['GET'])
def dashboard():
    news_data = fetch_news()
    search_query = request.args.get('search', '').lower()
    month_filter = request.args.get('month', '')

    filtered_news = news_data
    if search_query:
        filtered_news = [n for n in filtered_news if search_query in n['title'].lower()]
    if month_filter:
        filtered_news = [n for n in filtered_news if n['date'].strftime('%Y-%m') == month_filter]

    unique_months = sorted(set(n['date'].strftime('%Y-%m') for n in news_data), reverse=True)

    return render_template('dashboard.html', news=filtered_news, search_query=search_query, unique_months=unique_months, selected_month=month_filter)

if __name__ == '__main__':
    app.run(debug=True)
