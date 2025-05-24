import asyncio
from data_collection.alvan_dc.news_fetcher import fetch_single_news
from data_collection.alvan_dc.historical_price import fetch_single_adjdaily
from data_collection.alvan_dc.fundamental_fetcher import fetch_single_fundamental
from data_collection.alvan_dc.ec_transcript_fetcher import fetch_single_ec_transcript
from config.api_config import MAX_articles
from datetime import datetime
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Union, Optional

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

    max_days = 40
    raw_data = asyncio.run(fetch_single_adjdaily(ticker, "full"))
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

def get_stock_fundamental_data(ticker: str, function: str = "OVERVIEW") -> dict:
    """
    Synchronously fetch fundamental data (e.g., OVERVIEW, INCOME_STATEMENT) for a single stock ticker.
    Internally calls the async `fetch_single_fundamental` function.

    Args:
        ticker (str): The stock ticker symbol, e.g., 'AAPL'.
        function (str): Type of fundamental data to retrieve. Options include:
                        'OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 
                        'CASH_FLOW', 'EARNINGS', or 'DIVIDENDS'.

    Returns:
        dict: A dictionary containing the fundamental data for the given ticker.
    """
    return asyncio.run(fetch_single_fundamental(ticker, function))

get_stock_fundamental_data._tool_config = {
    "name": "fetch_stock_fundamental_data",
    "description": (
        "Fetches fundamental data for a single stock ticker. "
        "Parameters:\n"
        "- ticker (string): The stock ticker symbol, e.g., 'AAPL'.\n"
        "- function (string, default='OVERVIEW'): Type of fundamental data to retrieve. "
        "Options include 'OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', "
        "'EARNINGS', or 'DIVIDENDS'."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "function": {
            "type": "string",
            "description": (
                "Type of fundamental data to retrieve: "
                "'OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', "
                "'CASH_FLOW', 'EARNINGS', or 'DIVIDENDS'."
            ),
            "default": "OVERVIEW"
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

# tools for bullish and bearish

# Bullish
# === Trend Following Indicators ===
def moving_average(ticker: str, today_date: str, window: int = 14, ma_type: str = "simple", price_type: str = "close") -> Dict[str, List[float]]:
    """
    Fetch historical prices for a stock and calculate moving average.
    Args:
        ticker: The stock ticker symbol, e.g., 'AAPL'.
        today: today's date, 'YYYY-MM-DD' e.g., '2024-01-01'.
        window: MA window (default: 14).
        ma_type: "simple" (SMA) or "exponential" (EMA).
        price_type: "open", "high", "low", "close" (default: "close").
    Returns:
        {"dates": [str], "values": [float]} (NaN values replaced with None).
    """
    # function from above
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    
    dates = sorted(historical.keys())
    prices = [float(historical[date][price_type]) for date in dates]
    
    # calculate MA
    if ma_type == "simple":
        ma_values = (
            pd.Series(prices)
            .rolling(window=window)
            .mean()
            .tolist()
        )
    elif ma_type == "exponential":
        ma_values = (
            pd.Series(prices)
            .ewm(span=window, adjust=False)
            .mean()
            .tolist()
        )
    else:
        raise ValueError("ma_type must be 'simple' or 'exponential'")
    
    ma_values = [None if np.isnan(x) else x for x in ma_values]
    
    return {"dates": dates, "values": ma_values}

moving_average._tool_config = {
    "name": "moving_average",
    "description": (
        "Fetches historical prices for a stock and calculates moving average (SMA/EMA).\n"
        "Parameters:\n"
        "- ticker (string): The stock ticker symbol, e.g., 'AAPL'.\n"
        "- today (string): Today's date, 'YYYY-MM-DD' e.g., '2024-01-01'.\n"
        "- window (integer): MA window (default: 14).\n"
        "- ma_type (string): 'simple' or 'exponential' moving average (default: 'simple').\n"
        "- price_type (string): 'open', 'high', 'low', or 'close' (default: 'close')."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today": {
            "type": "string",
            "description": "Today's date in 'YYYY-MM-DD' format, e.g., '2024-01-01'."
        },
        "window": {
            "type": "integer",
            "default": 14,
            "description": "The moving average window size (default: 14)."
        },
        "ma_type": {
            "type": "string",
            "default": "simple",
            "description": "Type of moving average: 'simple' (SMA) or 'exponential' (EMA)."
        },
        "price_type": {
            "type": "string",
            "default": "close",
            "description": "Price type to use: 'open', 'high', 'low', or 'close'."
        }
    }
}

def macd(ticker: str, today_date: str, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> dict:
    """
    Fetches historical prices and computes Moving Average Convergence Divergence (MACD).
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        fast_period: Fast EMA period (default: 12).
        slow_period: Slow EMA period (default: 26).
        signal_period: Signal line period (default: 9).
    
    Returns:
        dict: MACD line, signal line, and histogram values for each date.
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    close_prices = [float(historical[date]["close"]) for date in dates]
    
    s = pd.Series(close_prices)
    fast_ema = s.ewm(span=fast_period, adjust=False).mean()
    slow_ema = s.ewm(span=slow_period, adjust=False).mean()
    macd_line = (fast_ema - slow_ema).tolist()
    signal_line = pd.Series(macd_line).ewm(span=signal_period, adjust=False).mean().tolist()
    histogram = (pd.Series(macd_line) - pd.Series(signal_line)).tolist()
    
    # Replace NaN with None
    macd_line = [None if np.isnan(x) else x for x in macd_line]
    signal_line = [None if np.isnan(x) else x for x in signal_line]
    histogram = [None if np.isnan(x) else x for x in histogram]
    
    return {
        "dates": dates,
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram,
        "parameters": {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
        }
    }

macd._tool_config = {
    "name": "macd",
    "description": (
        "Calculates the Moving Average Convergence Divergence (MACD) indicator.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- fast_period (integer): Fast EMA period (default: 12).\n"
        "- slow_period (integer): Slow EMA period (default: 26).\n"
        "- signal_period (integer): Signal line period (default: 9).\n"
        "\n"
        "Returns MACD line, signal line, and histogram values."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "fast_period": {
            "type": "integer",
            "default": 12,
            "description": "Period for fast exponential moving average (default: 12)."
        },
        "slow_period": {
            "type": "integer",
            "default": 26,
            "description": "Period for slow exponential moving average (default: 26)."
        },
        "signal_period": {
            "type": "integer",
            "default": 9,
            "description": "Period for signal line exponential moving average (default: 9)."
        }
    }
}

def trend_direction(ticker: str, today_date: str, window: int = 20) -> dict:
    """
    Determines trend direction and strength using moving averages.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        window: Analysis window period (default: 20).
    
    Returns:
        dict: Trend direction ('uptrend', 'downtrend', 'neutral') and strength (0-100).
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    close_prices = [float(historical[date]["close"]) for date in dates]
    
    short_ma = pd.Series(close_prices).rolling(window=window//2).mean().tolist()
    long_ma = pd.Series(close_prices).rolling(window=window).mean().tolist()
    
    trends = []
    strengths = []
    
    for i in range(len(close_prices)):
        if pd.isna(short_ma[i]) or pd.isna(long_ma[i]):
            trends.append("neutral")
            strengths.append(0)
            continue
        
        if short_ma[i] > long_ma[i]:
            if i > 0:
                momentum = (close_prices[i] - close_prices[i-1]) / close_prices[i-1] if close_prices[i-1] != 0 else 0
                ma_diff = (short_ma[i] - long_ma[i]) / long_ma[i] if long_ma[i] != 0 else 0
                strength = min(100, max(0, 50 + 50 * (momentum + ma_diff)))
            else:
                strength = 50
            trends.append("uptrend")
            strengths.append(strength)
        elif short_ma[i] < long_ma[i]:
            if i > 0:
                momentum = (close_prices[i] - close_prices[i-1]) / close_prices[i-1] if close_prices[i-1] != 0 else 0
                ma_diff = (short_ma[i] - long_ma[i]) / long_ma[i] if long_ma[i] != 0 else 0
                strength = min(100, max(0, 50 - 50 * (momentum + ma_diff)))
            else:
                strength = 50
            trends.append("downtrend")
            strengths.append(strength)
        else:
            trends.append("neutral")
            strengths.append(0)
    
    return {
        "dates": dates,
        "trend": trends,
        "strength": strengths,
        "window": window
    }

trend_direction._tool_config = {
    "name": "trend_direction",
    "description": (
        "Determines trend direction and strength using moving averages.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- window (integer): Analysis window period (default: 20).\n"
        "\n"
        "Returns trend direction and strength (0-100) for each date."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "window": {
            "type": "integer",
            "default": 20,
            "description": "Number of periods for trend analysis (default: 20)."
        }
    }
}

# === Breakout Detection ===
def trend_direction(ticker: str, today_date: str, window: int = 20) -> dict:
    """
    Determines trend direction and strength using moving averages.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        window: Analysis window period (default: 20).
    
    Returns:
        dict: Trend direction ('uptrend', 'downtrend', 'neutral') and strength (0-100).
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    close_prices = [float(historical[date]["close"]) for date in dates]
    
    short_ma = pd.Series(close_prices).rolling(window=window//2).mean().tolist()
    long_ma = pd.Series(close_prices).rolling(window=window).mean().tolist()
    
    trends = []
    strengths = []
    
    for i in range(len(close_prices)):
        if pd.isna(short_ma[i]) or pd.isna(long_ma[i]):
            trends.append("neutral")
            strengths.append(0)
            continue
        
        if short_ma[i] > long_ma[i]:
            if i > 0:
                momentum = (close_prices[i] - close_prices[i-1]) / close_prices[i-1] if close_prices[i-1] != 0 else 0
                ma_diff = (short_ma[i] - long_ma[i]) / long_ma[i] if long_ma[i] != 0 else 0
                strength = min(100, max(0, 50 + 50 * (momentum + ma_diff)))
            else:
                strength = 50
            trends.append("uptrend")
            strengths.append(strength)
        elif short_ma[i] < long_ma[i]:
            if i > 0:
                momentum = (close_prices[i] - close_prices[i-1]) / close_prices[i-1] if close_prices[i-1] != 0 else 0
                ma_diff = (short_ma[i] - long_ma[i]) / long_ma[i] if long_ma[i] != 0 else 0
                strength = min(100, max(0, 50 - 50 * (momentum + ma_diff)))
            else:
                strength = 50
            trends.append("downtrend")
            strengths.append(strength)
        else:
            trends.append("neutral")
            strengths.append(0)
    
    return {
        "dates": dates,
        "trend": trends,
        "strength": strengths,
        "window": window
    }

trend_direction._tool_config = {
    "name": "trend_direction",
    "description": (
        "Determines trend direction and strength using moving averages.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- window (integer): Analysis window period (default: 20).\n"
        "\n"
        "Returns trend direction and strength (0-100) for each date."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "window": {
            "type": "integer",
            "default": 20,
            "description": "Number of periods for trend analysis (default: 20)."
        }
    }
}

# === Momentum Confirmation ===

def rsi(ticker: str, today_date: str, period: int = 14) -> dict:
    """
    Calculates Relative Strength Index (RSI) for a stock.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        period: RSI calculation period (default: 14).
    
    Returns:
        dict: RSI values for each date.
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    close_prices = [float(historical[date]["close"]) for date in dates]
    
    s = pd.Series(close_prices)
    delta = s.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi_values = (100 - (100 / (1 + rs))).tolist()
    
    rsi_values = [None if pd.isna(x) else x for x in rsi_values]
    
    return {
        "dates": dates,
        "rsi": rsi_values,
        "period": period
    }

rsi._tool_config = {
    "name": "rsi",
    "description": (
        "Calculates Relative Strength Index (RSI) for a stock.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- period (integer): RSI calculation period (default: 14).\n"
        "\n"
        "Returns RSI values (0-100) for each date."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "period": {
            "type": "integer",
            "default": 14,
            "description": "RSI calculation period (default: 14)."
        }
    }
}

# === Pullback Signals ===
def support_resistance_levels(ticker: str, today_date: str, window: int = 20, num_levels: int = 3) -> dict:
    """
    Identifies key support and resistance levels for a stock.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        window: Lookback window for identifying levels (default: 20).
        num_levels: Number of levels to identify (default: 3).
    
    Returns:
        dict: Support and resistance levels with their values.
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    
    highs = [float(historical[date]["high"]) for date in dates]
    lows = [float(historical[date]["low"]) for date in dates]
    closes = [float(historical[date]["close"]) for date in dates]
    
    supports = []
    resistances = []
    
    for i in range(window // 2, len(closes) - window // 2):
        window_lows = lows[max(0, i - window // 2):min(len(lows), i + window // 2 + 1)]
        if lows[i] == min(window_lows):
            supports.append((dates[i], lows[i]))
            
        window_highs = highs[max(0, i - window // 2):min(len(highs), i + window // 2 + 1)]
        if highs[i] == max(window_highs):
            resistances.append((dates[i], highs[i]))
    
    supports.sort(key=lambda x: x[1])
    resistances.sort(key=lambda x: x[1], reverse=True)
    
    support_levels = [level[1] for level in supports[:min(num_levels, len(supports))]]
    resistance_levels = [level[1] for level in resistances[:min(num_levels, len(resistances))]]
    
    return {
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "last_date": dates[-1] if dates else None,
        "parameters": {
            "window": window,
            "num_levels": num_levels
        }
    }

support_resistance_levels._tool_config = {
    "name": "support_resistance_levels",
    "description": (
        "Identifies key support and resistance levels for a stock.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- window (integer): Lookback window for identifying levels (default: 20).\n"
        "- num_levels (integer): Number of levels to identify (default: 3).\n"
        "\n"
        "Returns identified support and resistance levels."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "window": {
            "type": "integer",
            "default": 20,
            "description": "Lookback window for identifying levels (default: 20)."
        },
        "num_levels": {
            "type": "integer",
            "default": 3,
            "description": "Number of levels to identify (default: 3)."
        }
    }
}

def candlestick_pattern_recognition(ticker: str, today_date: str) -> dict:
    """
    Recognizes common candlestick patterns in stock price data.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
    
    Returns:
        dict: Identified candlestick patterns for each date.
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    
    opens = [float(historical[date]["open"]) for date in dates]
    highs = [float(historical[date]["high"]) for date in dates]
    lows = [float(historical[date]["low"]) for date in dates]
    closes = [float(historical[date]["close"]) for date in dates]
    
    patterns = {
        "doji": [False] * len(closes),
        "hammer": [False] * len(closes),
        "inverted_hammer": [False] * len(closes),
        "bullish_engulfing": [False] * len(closes),
        "bearish_engulfing": [False] * len(closes),
        "morning_star": [False] * len(closes),
        "evening_star": [False] * len(closes),
        "shooting_star": [False] * len(closes)
    }
    
    for i in range(len(closes)):
        if i == 0:
            continue
            
        body_size = abs(closes[i] - opens[i])
        upper_shadow = highs[i] - max(opens[i], closes[i])
        lower_shadow = min(opens[i], closes[i]) - lows[i]
        total_range = highs[i] - lows[i]
        
        if total_range > 0 and body_size / total_range < 0.1:
            patterns["doji"][i] = True
            
        if (closes[i] > opens[i] and body_size > 0
            and lower_shadow >= 2 * body_size
            and upper_shadow < 0.2 * body_size):
            patterns["hammer"][i] = True
            
        if (closes[i] > opens[i] and body_size > 0
            and upper_shadow >= 2 * body_size
            and lower_shadow < 0.2 * body_size):
            patterns["inverted_hammer"][i] = True
            
        if (closes[i] < opens[i] and body_size > 0
            and upper_shadow >= 2 * body_size
            and lower_shadow < 0.2 * body_size):
            patterns["shooting_star"][i] = True
            
        if i >= 1:
            if (closes[i-1] < opens[i-1]
                and closes[i] > opens[i]
                and opens[i] <= closes[i-1]
                and closes[i] >= opens[i-1]):
                patterns["bullish_engulfing"][i] = True
                
            if (closes[i-1] > opens[i-1]
                and closes[i] < opens[i]
                and opens[i] >= closes[i-1]
                and closes[i] <= opens[i-1]):
                patterns["bearish_engulfing"][i] = True
        
        if i >= 2:
            if (closes[i-2] < opens[i-2]
                and abs(closes[i-1] - opens[i-1]) < 0.3 * abs(closes[i-2] - opens[i-2])
                and closes[i] > opens[i]
                and (closes[i] - opens[i]) > 0.6 * (opens[i-2] - closes[i-2])
                and max(opens[i-1], closes[i-1]) < closes[i-2]):
                patterns["morning_star"][i] = True
                
            if (closes[i-2] > opens[i-2]
                and abs(closes[i-1] - opens[i-1]) < 0.3 * abs(closes[i-2] - opens[i-2])
                and closes[i] < opens[i]
                and (opens[i] - closes[i]) > 0.6 * (closes[i-2] - opens[i-2])
                and min(opens[i-1], closes[i-1]) > closes[i-2]):
                patterns["evening_star"][i] = True
    
    result = {"dates": dates}
    result.update(patterns)
    return result

candlestick_pattern_recognition._tool_config = {
    "name": "candlestick_pattern_recognition",
    "description": (
        "Recognizes common candlestick patterns in stock price data.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "\n"
        "Returns identified candlestick patterns for each date."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        }
    }
}

# Bearish
# === Reversal Indicators ===
# rsi and macd from above

# === Divergence Detection ===
def divergence_detection(ticker: str, today_date: str, indicator: str = "macd", lookback_period: int = 14) -> dict:
    """
    Detects divergences between price and technical indicators.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        indicator: Indicator to use ('macd', 'rsi') (default: 'macd').
        lookback_period: Period to analyze for divergences (default: 14).
    
    Returns:
        dict: Detected bullish and bearish divergences.
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    closes = [float(historical[date]["close"]) for date in dates]
    
    bullish_divergences = []
    bearish_divergences = []
    
    if indicator == "macd":
        macd_data = macd(ticker, today_date)
        indicator_values = macd_data["macd_line"]
    elif indicator == "rsi":
        rsi_data = rsi(ticker, today_date)
        indicator_values = rsi_data["rsi"]
    
    for i in range(lookback_period, len(closes)):
        price_slope = closes[i] - closes[i-lookback_period]
        indicator_slope = indicator_values[i] - indicator_values[i-lookback_period]
        
        if price_slope < 0 and indicator_slope > 0:
            bullish_divergences.append(dates[i])
        elif price_slope > 0 and indicator_slope < 0:
            bearish_divergences.append(dates[i])
    
    return {
        "bullish_divergences": bullish_divergences,
        "bearish_divergences": bearish_divergences,
        "indicator": indicator,
        "lookback_period": lookback_period
    }

divergence_detection._tool_config = {
    "name": "divergence_detection",
    "description": (
        "Detects divergences between price and technical indicators.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- indicator (string): Indicator to use ('macd', 'rsi') (default: 'macd').\n"
        "- lookback_period (integer): Period to analyze for divergences (default: 14).\n"
        "\n"
        "Returns detected bullish and bearish divergences."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "indicator": {
            "type": "string",
            "default": "macd",
            "description": "Indicator to use for divergence detection (default: 'macd')."
        },
        "lookback_period": {
            "type": "integer",
            "default": 14,
            "description": "Period to analyze for divergences (default: 14)."
        }
    }
}

# === Breakdown Signals ===
# breakout_detection and bollinger_bands from above

# === Volatility and Weakness ===
def atr(ticker: str, today_date: str, period: int = 14) -> dict:
    """
    Calculates Average True Range (ATR) for a stock.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        today_date: Cutoff date in 'YYYY-MM-DD' format.
        period: ATR calculation period (default: 14).
    
    Returns:
        dict: ATR values for each date.
    """
    price_data = get_stock_price_history(ticker, today_date)
    historical = price_data[ticker]["historical"]
    dates = sorted(historical.keys())
    
    highs = [float(historical[date]["high"]) for date in dates]
    lows = [float(historical[date]["low"]) for date in dates]
    closes = [float(historical[date]["close"]) for date in dates]
    
    true_ranges = []
    for i in range(1, len(closes)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i-1])
        low_close = abs(lows[i] - closes[i-1])
        true_ranges.append(max(high_low, high_close, low_close))
    
    atr_values = pd.Series(true_ranges).rolling(window=period).mean().tolist()
    atr_values = [None] + [None if pd.isna(x) else x for x in atr_values]  # Pad first day
    
    return {
        "dates": dates,
        "atr": atr_values,
        "period": period
    }

atr._tool_config = {
    "name": "atr",
    "description": (
        "Calculates Average True Range (ATR) for a stock.\n"
        "Parameters:\n"
        "- ticker (string): Stock ticker symbol (e.g., 'AAPL').\n"
        "- today_date (string): Cutoff date in 'YYYY-MM-DD' format.\n"
        "- period (integer): ATR calculation period (default: 14).\n"
        "\n"
        "Returns ATR values for each date."
    ),
    "parameters": {
        "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g., 'AAPL'."
        },
        "today_date": {
            "type": "string",
            "description": "Cutoff date in 'YYYY-MM-DD' format."
        },
        "period": {
            "type": "integer",
            "default": 14,
            "description": "ATR calculation period (default: 14)."
        }
    }
}

# === Pattern Recognition ===
# candlestick_pattern_recognition from above