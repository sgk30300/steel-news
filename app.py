from flask import Flask, render_template, request
from utils.fetch_news import fetch_steel_news

app = Flask(__name__)

@app.route("/")
def dashboard():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    source = request.args.get("source", "")

    news_items = fetch_steel_news(keyword=keyword, category=category, month=month, source=source)
    return render_template("dashboard.html", news_items=news_items, keyword=keyword, category=category, month=month, source=source)

if __name__ == "__main__":
    app.run(debug=True)