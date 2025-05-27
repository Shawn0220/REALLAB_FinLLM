import asyncio
from data_collection.alvan_dc.news_fetcher import fetch_single_news
from data_collection.alvan_dc.historical_price import fetch_single_adjdaily
from data_collection.alvan_dc.fundamental_fetcher import fetch_single_fundamental
from data_collection.alvan_dc.ec_transcript_fetcher import fetch_single_ec_transcript
from config.api_config import MAX_articles
from datetime import datetime
from functions.local_data_loader import fetch_single_adjdaily_locally, fetch_fundamental_summary
import re
from datetime import datetime


def normalize_time_string(t: str) -> str:
    """
    Normalize a time string into 'YYYYMMDDTHHMM' format.

    - Accepts date with '-', '/', '.' separators
    - Allows missing 'T' → defaults to T0000 (midnight)
    - Extracts at most 4 digits from time part; left-pads if too short
    - Validates date and time ranges

    Examples:
        '2024-01-08T23:59:59' → '20240108T2359'
        '2024-01-08' → '20240108T0000'
        '20240108' → '20240108T0000'
        '2024/01/08T9' → '20240108T0009'

    Raises:
        ValueError if date/time format is invalid
    """
    # Step 1: Remove separators from date
    t_clean = re.sub(r"[-/\.]", "", t)

    # Step 2: Ensure 'T' is present; if not, default to midnight
    if "T" not in t_clean:
        t_clean += "T0000"

    date_part, time_part = t_clean.split("T", 1)

    # Step 3: Extract and validate date (first 8 digits)
    if len(date_part) < 8 or not date_part[:8].isdigit():
        raise ValueError(f"Date must start with 8 digits (YYYYMMDD), got: '{date_part}'")

    date_part = date_part[:8]
    try:
        datetime.strptime(date_part, "%Y%m%d")
    except ValueError:
        raise ValueError(f"Invalid calendar date: {date_part}")

    # Step 4: Normalize time part
    time_digits = re.sub(r"\D", "", time_part)[:4].zfill(4)

    if len(time_digits) != 4 or not time_digits.isdigit():
        raise ValueError(f"Invalid time format after 'T': '{time_part}'")

    hour, minute = int(time_digits[:2]), int(time_digits[2:])
    if hour >= 24 or minute >= 60:
        raise ValueError(f"Invalid time value: HH={hour}, MM={minute}")

    return f"{date_part}T{time_digits}"




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
    time_from = normalize_time_string(time_from)
    time_to = normalize_time_string(time_to)
    # print(time_from, "*********", time_to)

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


def get_stock_price_history(ticker: str, today_date: str) -> dict:
    """
    Fetch historical adjusted daily stock price data for a stock ticker,
    filtering out future data beyond `today_date` to prevent data leakage.

    Args:
        ticker (str): Stock ticker symbol, e.g., 'TSLA'.
        outputsize (str): 'compact' or 'full'.
        today_date (str): Upper bound (inclusive) for returned dates, e.g., '2024-01-25'.

    Returns:
        dict: Filtered historical data, e.g., {'TSLA': {date: price_data, ...}}
    """

    max_days = 20
    raw_data = fetch_single_adjdaily_locally(ticker)
    # print(raw_data)
    all_dates = list(raw_data[ticker].keys())
    all_dates_sorted = sorted(all_dates, reverse=True)  # most recent first

    cutoff_dt = datetime.strptime(today_date, "%Y-%m-%d")
    
    historical = {}
    today_open = None
    count = 0

    for date_str in all_dates_sorted:
        date_dt = datetime.strptime(date_str, "%Y-%m-%d")
        if date_dt < cutoff_dt:
            # T 日之前的历史数据，作为上下文
            historical[date_str] = {
                'close': raw_data[ticker][date_str]['4. close'],
                'volume': raw_data[ticker][date_str]['6. volume']
            }
            count += 1
            if count >= max_days:
                break
        elif date_dt == cutoff_dt:
            # T 日的开盘价
            today_open = raw_data[ticker][date_str]['1. open']

    return {
        ticker: {
            'historical': dict(sorted(historical.items())),  # 按时间正序
            'today_open': today_open
        }
    }

get_stock_price_history._tool_config = {
    "name": "fetch_stock_price_history",
    "description": (
        "Fetches historical adjusted daily stock price data for a single stock ticker. "
        "Requires the following parameters: "
        "`ticker` is the stock ticker symbol (e.g., 'AAPL'), type string; "
        # "`outputsize` determines how much historical data to return, type string, "
        "use 'compact' to get the latest 100 data points or 'full' to get the complete history."
        "`today_date` is the cutoff date to prevent future data leakage (e.g., '2021-02-03'), type string in 'YYYY-MM-DD' format; only data on or before this date will be returned."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        # "outputsize": {
        #     "type": "string",
        #     "description": "Amount of historical data to retrieve: 'compact' (latest 100 points) or 'full' (entire history).",
        #     "default": "compact"
        # }
    }
}

def get_stock_fundamental_data(ticker: str, today: str) -> dict:
    """
    Synchronously fetch fundamental data (e.g., OVERVIEW, INCOME_STATEMENT) for a single stock ticker.
    Internally calls the async `fetch_single_fundamental` function.

    Args:
        ticker (str): The stock ticker symbol, e.g., 'AAPL'.
        today (str): today's date, 'YYYY-MM-DD' e.g., '2023-03-11'.

    Returns:
        dict: A dictionary containing the fundamental data for the given ticker.
    """
    return fetch_fundamental_summary(ticker, today)
# asyncio.run(fetch_single_fundamental(ticker, function))

get_stock_fundamental_data._tool_config = {
    "name": "fetch_stock_fundamental_data",
    "description": (
        "Fetches fundamental data for a single stock ticker. "
        "Parameters:\n"
        "- ticker (string): The stock ticker symbol, e.g., 'AAPL'.\n"
        "- today (string): today's date, 'YYYY-MM-DD' e.g., '2023-03-11'"
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today": {
            "type": "string",
            "description": (
                "today's date, 'YYYY-MM-DD' e.g., '2023-03-11'"
            )
        }
    }
}


def get_earning_call_transcript(ticker: str, quarter: str) -> dict:
    """
    Synchronously fetch earnings call transcript for a single stock ticker and fiscal quarter.
    Internally calls the async `fetch_single_ec_transcript` function.

    Args:
        ticker (str): The stock ticker symbol, e.g., 'AAPL'.
        quarter (str): Fiscal quarter in the format 'YYYYQM', e.g., '2023Q4'.

    Returns:
        dict: A dictionary containing the earnings call transcript for the specified ticker and quarter.
    """
    return asyncio.run(fetch_single_ec_transcript(ticker, quarter))

get_earning_call_transcript._tool_config = {
    "name": "fetch_earning_call_transcript",
    "description": (
        "Fetches the earnings call transcript for a specific fiscal quarter. "
        "Parameters:\n"
        "- ticker (string): The stock ticker symbol, e.g., 'AAPL'.\n"
        "- quarter (string): Fiscal quarter in format 'YYYYQM', e.g., '2023Q4'."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "quarter": {
            "type": "string",
            "description": "Fiscal quarter in format 'YYYYQM', e.g., '2023Q4'."
        }
    }
}