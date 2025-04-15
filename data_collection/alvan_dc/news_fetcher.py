import asyncio
import aiohttp

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
