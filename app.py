import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

RSS_FEEDS = {
    'Google News': 'https://news.google.com/rss/search?q=steel&hl=en-IN&gl=IN&ceid=IN:en',
    'Economic Times': 'https://economictimes.indiatimes.com/rssfeeds/industry/indl-goods-/-svs/steel/rssfeeds/13376752.cms',
    'Mint': 'https://www.livemint.com/rss/companies',
    'GMK Center': 'https://gmk.center/en/feed/'
}

def fetch_steel_news(keyword='', category='', month='', source=''):
    articles = []

    for src, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = BeautifulSoup(entry.get('summary', ''), 'html.parser').text
            date_published = entry.get('published', entry.get('updated', ''))

            # Handle multiple time formats
            try:
                if 'GMT' in date_published:
                    date_obj = datetime.strptime(date_published.replace(' GMT', ''), '%a, %d %b %Y %H:%M:%S')
                elif '+' in date_published:
                    date_obj = datetime.strptime(date_published.split('+')[0].strip(), '%a, %d %b %Y %H:%M:%S')
                else:
                    date_obj = datetime.strptime(date_published, '%a, %d %b %Y %H:%M:%S')
            except:
                date_obj = datetime.now()

            if 'steel' not in title.lower():
                continue

            articles.append({
                'date': date_obj,
                'source': src,
                'title': title,
                'summary': summary,
                'link': link
            })

    # Apply filters
    if keyword:
        articles = [a for a in articles if keyword.lower() in a['title'].lower() or keyword.lower() in a['summary'].lower()]
    if category:
        articles = [a for a in articles if category.lower() in a['title'].lower()]
    if source:
        articles = [a for a in articles if source.lower() in a['source'].lower()]
    if month:
        articles = [a for a in articles if a['date'].strftime('%Y-%m') == month]

    return sorted(articles, key=lambda x: x['date'], reverse=True)
