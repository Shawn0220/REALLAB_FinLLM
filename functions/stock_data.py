import asyncio
from data_collection.alvan_dc.news_fetcher import fetch_single_news
from data_collection.alvan_dc.historical_price import fetch_ticker_symbol
from config.api_config import MAX_articles


# === Tool 1: Company Info ===
def data_collect_company_info(stock_name: str) -> str:
    """
    Collects company information for the given stock.
    (This is a placeholder. In practice, you could call APIs like Yahoo Finance, Alpha Vantage, etc.)
    """
    return f"{stock_name} is a tech company founded in 2005."

data_collect_company_info._tool_config = {
    "name": "data_collect_company_info",
    "description": "Collects company information for the given stock."
}


# === Tool 2: Stock Price History ===
def data_collect_stock_price_history(stock_name: str) -> list:
    """
    Collects historical stock price data for the given stock.
    (This is a placeholder. Use real price history in practice.)
    """
    return [120, 123, 119, 125, 130]

data_collect_stock_price_history._tool_config = {
    "name": "data_collect_stock_price_history",
    "description": "Collects historical stock price data for a given stock."
}


# === Tool 3: Social Sentiment ===
def data_collect_social_sentiment(stock_name: str) -> str:
    """
    Collects social media sentiment data for the given stock.
    (This is a placeholder. You can integrate sentiment analysis tools here.)
    """
    return "Mixed, trending positive."

data_collect_social_sentiment._tool_config = {
    "name": "data_collect_social_sentiment",
    "description": "Collects social media sentiment data for a given stock."
}



# functions/stock_data.py

def data_collect(stock_name):
    """
    Collects general stock data.
    """
    return {
        "company_info": f"{stock_name} is a tech company founded in 2005.",
        "stock_price_history": [120, 123, 119, 125, 130],
        "social_media_sentiment": "Mixed, trending positive."
    }

data_collect._tool_config = {
    "name": "data_collect",
    "description": "Collects company info, stock price history, and sentiment."
}




def get_moving_average(stock_name: str, window: int = 3) -> float:
    return sum([120, 123, 119][-window:]) / window

get_moving_average._tool_config = {
    "name": "get_moving_average",
    "description": "Returns the moving average of the stock price for a given window."
}



def get_stock_news_sentiment(ticker: str, time_from: str, time_to: str, sort: str = "RELEVANCE") -> dict:
    """
    Synchronously fetch news for a single stock ticker.
    Internally calls the async `fetch_single_news` function.
    """
    full_result = asyncio.run(fetch_single_news(ticker, time_from, time_to, sort))
    simplified = {}
    
    for ticker, articles in full_result.items():
        simplified[ticker] = []
        cnt = 0
        for article in articles:
            cnt += 1
            simplified_article = {
                "title": article.get("title"),
                # "url": article.get("url"),
                # "time_published": article.get("time_published"),
                "summary": article.get("summary"),
                "source": article.get("source"),
                "overall_sentiment": article.get("overall_sentiment_label") + " score-" + str(article.get("overall_sentiment_score"))
                # "ticker_sentiment": article.get("ticker_sentiment")
            }
            simplified[ticker].append(simplified_article)
            if cnt >= MAX_articles:
                break
    return simplified

get_stock_news_sentiment._tool_config = {
    "name": "fetch_single_news",
    "description": (
        "Fetches news articles for a single stock ticker within a specified date range. "
        "Requires the following parameters: "
        "`ticker` is the stock ticker symbol (e.g., 'AAPL'); "
        "`time_from` is the start time in ISO format (e.g., '20240101T0130'); "
        "`time_to` is the end time in ISO format (e.g., '20250401T0130'); "
        "`sort` determines the sorting order for results (e.g., 'RELEVANCE' or 'LATEST'; default is 'RELEVANCE')."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "time_from": {
            "type": "string",
            "description": "Start time in ISO format, e.g., '20240101T0130'."
        },
        "time_to": {
            "type": "string",
            "description": "End time in ISO format, e.g., '20250401T0130'."
        },
        "sort": {
            "type": "string",
            "description": "Sorting order for results, such as 'RELEVANCE' or 'LATEST'.",
            "default": "RELEVANCE"
        }
    }
}


def get_stock_price_history(ticker: str, outputsize: str = "compact") -> dict:
    """
    Synchronously fetch historical adjusted daily stock price data for a single stock ticker.
    Internally calls the async `fetch_ticker_symbol` function.

    Args:
        ticker (str): The stock ticker symbol, e.g., 'AAPL'.
        outputsize (str): 'compact' for latest 100 points, 'full' for full history. Considering context window, better not to use 'full'

    Returns:
        dict: A dictionary containing the historical stock price data.
    """
    return asyncio.run(fetch_ticker_symbol(ticker, outputsize))

get_stock_price_history._tool_config = {
    "name": "fetch_stock_price_history",
    "description": (
        "Fetches historical adjusted daily stock price data for a single stock ticker. "
        "Requires the following parameters: "
        "`ticker` is the stock ticker symbol (e.g., 'AAPL'); "
        "`outputsize` determines how much historical data to return; "
        "use 'compact' to get the latest 100 data points or 'full' to get the complete history."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "outputsize": {
            "type": "string",
            "description": "Amount of historical data to retrieve: 'compact' (latest 100 points) or 'full' (entire history).",
            "default": "compact"
        }
    }
}
