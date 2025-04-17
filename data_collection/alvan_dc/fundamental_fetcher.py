import asyncio
import aiohttp
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config.api_config import api_keys

class AlphaVantageFundamentalFetcher:
    def __init__(self, api_key:str=api_keys["alphavantage"], max_concurrent_requests:int=25):
        """
        Initialize fndemental data fetcher

        Args:
            api_key (str): Your Alpha Vantage API key.
            max_concurrent_requests (int): Maximum number of concurrent API requests.

        """
        self.api_key = api_key
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def fetch_fundamental(self, ticker:str, function:str, session:aiohttp.ClientSession = None) -> dict:
        """
        Fetch fundamental data for a single ticker.

        Args:
            ticker (str): Ticker symbol.
            function (str): 'OVERVIEW'/'INCOME_STATEMENT'/'BALANCE_SHEET'/'CASH_FLOW'/'EARNINGS'/'DIVIDENDS'
            session: Existing aiohttp session.
        
        Returns:
            dict: A dictionary mapping the ticker to its corresponding fundamental data.
        """

        url = f'https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={self.api_key}'

        if session is None:
            async with aiohttp.ClientSession() as new_session:
                async with self.semaphore:
                    async with new_session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data
                        return {ticker: None}
        else:
            async with self.semaphore:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    return {ticker: None}

async def fetch_single_fundamental(ticker:str, function:str) -> dict:
    """
    Fetch fundamental data for a single ticker.

    Args:
        ticker (str): Ticker symbol.
        function (str): 'OVERVIEW'/'INCOME_STATEMENT'/'BALANCE_SHEET'/'CASH_FLOW'/'EARNINGS'/'DIVIDENDS'
    
    Returns:
        dict: A dictionary mapping the ticker to its corresponding fundamental data.
    """
    fetcher = AlphaVantageFundamentalFetcher()
    async with aiohttp.ClientSession() as session:
        return await fetcher.fetch_fundamental(ticker, function=function, session=session)