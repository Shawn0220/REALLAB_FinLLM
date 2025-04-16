
import asyncio

import asyncio
import aiohttp
import os


ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")
print(ALPHAVANTAGE_API_KEY)


class AlphaVantageNewsFetcher:
    def __init__(self, api_key, time_from, time_to, sort="RELEVANCE", max_concurrent_requests=25):
        """
        Initialize the news fetcher.
        
        Args:
            api_key (str): Your Alpha Vantage API key.
            max_concurrent_requests (int): Maximum number of concurrent API requests.

        """
        self.api_key = api_key
        self.time_from = time_from
        self.time_to = time_to
        self.sort = sort
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def fetch_news(self, ticker, session=None):
        """
        Fetch news sentiment for a single ticker.

        Args:
            ticker (str): Ticker symbol.
            session: Existing aiohttp session.

        Returns:
            dict: A dictionary mapping the ticker to its news data.
        """
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&time_from={self.time_from}&time_to={self.time_to}&sort={self.sort}&apikey={self.api_key}'
        if session is None:
            async with aiohttp.ClientSession() as new_session:
                async with self.semaphore:
                    async with new_session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {ticker: data.get("feed", [])}
                        return {ticker: None}
        else:
            async with self.semaphore:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {ticker: data.get("feed", [])}
                    return {ticker: None}


async def fetch_all_news(tickers, api_key, time_from, time_to, sort="RELEVANCE", max_concurrent_requests=25):
    """
    Fetch news for a list of company of ticker using AlphaVantageNewsFetcher.

    Args:
        tickers (list): List of ticker symbols.
        api_key (str): Alpha Vantage API key.
        time_from (str): Start time.
        time_to (str): End time.
        sort (str): Sort order(Latest, Earliest) 
        max_concurrent_requests (int): Max concurrent requests.

    Returns:
        dict: Dictionary of ticker to news data.
    """
    fetcher = AlphaVantageNewsFetcher(api_key, time_from, time_to, sort, max_concurrent_requests)
    results = {}

    async with aiohttp.ClientSession() as session:
        tasks = [fetcher.fetch_news(ticker, session=session) for ticker in tickers]
        responses = await asyncio.gather(*tasks)

        for r in responses:
            results.update(r)

    return results


async def fetch_single_news(ticker, time_from, time_to, sort="RELEVANCE"):
    """
    Fetch news for a single ticker symbol.

    Args:
        ticker (str): Stock ticker.
        time_from (str): Start time.
        time_to (str): End time.
        sort (str): Sorting order.

    Returns:
        dict: Ticker -> News feed list
    """

    fetcher = AlphaVantageNewsFetcher(ALPHAVANTAGE_API_KEY, time_from, time_to, sort)
    async with aiohttp.ClientSession() as session:
        return await fetcher.fetch_news(ticker, session=session)


def get_stock_news_sentiment(ticker: str, time_from: str, time_to: str, sort: str = "RELEVANCE") -> dict:
    """
    Synchronously fetch news for a single stock ticker.
    Internally calls the async `fetch_single_news` function.
    """
    full_result = asyncio.run(fetch_single_news(ticker, time_from, time_to, sort))
    simplified = {}
    for ticker, articles in full_result.items():
        simplified[ticker] = []
        for article in articles:
            simplified_article = {
                "title": article.get("title"),
                # "url": article.get("url"),
                # "time_published": article.get("time_published"),
                "summary": article.get("summary"),
                "source": article.get("source"),
                "overall_sentiment": article.get("overall_sentiment_label") + " score-" + str(article.get("overall_sentiment_score"))
                # "ticker_sentiment": article.get("ticker_sentiment")  # 可选：可以注释掉这一行
            }
            simplified[ticker].append(simplified_article)
    return simplified


a = get_stock_news_sentiment('TSLA','20240101T0130','20250401T0130','RELEVANCE')
print(a)