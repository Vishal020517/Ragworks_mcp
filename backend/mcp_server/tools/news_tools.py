import requests


def get_stock_news(query: str) -> list:
    """
    Fetch latest news (using free API like NewsAPI or fallback)
    """
    try:
        url = f"https://newsapi.org/v2/everything?q={query}&pageSize=5&apiKey=82207354f23d4052b6f2ad78e1950f1e"

        response = requests.get(url)
        data = response.json()

        articles = []

        for article in data.get("articles", []):
            articles.append({
                "title": article["title"],
                "source": article["source"]["name"]
            })

        return articles

    except Exception as e:
        return [{"error": str(e)}]