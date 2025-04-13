def data_collect_company_info(stock_name: str) -> str:
    """
    Collects company information for the given stock.
    (This is a placeholder. In practice, you could call APIs like Yahoo Finance, Alpha Vantage, etc.)
    """
    return f"{stock_name} is a tech company founded in 2005."


def data_collect_stock_price_history(stock_name: str) -> list:
    """
    Collects historical stock price data for the given stock.
    (This is a placeholder. Use real price history in practice.)
    """
    return [120, 123, 119, 125, 130]


def data_collect_social_sentiment(stock_name: str) -> str:
    """
    Collects social media sentiment data for the given stock.
    (This is a placeholder. You can integrate sentiment analysis tools here.)
    """
    return "Mixed, trending positive."


def data_collect(stock_name: str) -> dict:
    """
    Gathers all data sources into one dictionary.
    """
    return {
        "company_info": data_collect_company_info(stock_name),
        "stock_price_history": data_collect_stock_price_history(stock_name),
        "social_media_sentiment": data_collect_social_sentiment(stock_name)
    }
