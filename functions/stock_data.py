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

# 提供函数注册所需元信息
data_collect._tool_config = {
    "name": "data_collect",
    "description": "Collects company info, stock price history, and sentiment."
}

# 用户也可以自己写函数
def get_moving_average(stock_name, window=3):
    return sum([120, 123, 119][-window:]) / window

get_moving_average._tool_config = {
    "name": "get_moving_average",
    "description": "Returns the moving average of the stock price for a given window."
}
