import asyncio
import aiohttp
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config.api_config import api_keys

class AlphaVantageHistPriceFetcher:
    def __init__(self, api_key: str = api_keys["alphavantage"], outputsize: str = "compact", datatype: str = "json", max_concurrent_requests: int = 25):
        """
        Initialize the daily price fetcher.
        
        Args:
            api_key (str): Your Alpha Vantage API key.
            outputsize (str): 'compact' for latest 100 points, 'full' for full history.
            datatype (str): 'json' or 'csv'.
            max_concurrent_requests (int): Max concurrent API calls allowed.

        """
        self.api_key = api_key
        self.outputsize = outputsize
        self.datatype = datatype
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)


    async def fetch_adjdaily(self, ticker: str, session: aiohttp.ClientSession = None) -> dict:
        """
        Fetch adjusted daily stock price data for a single ticker.

        Args:
            ticker (str): Ticker symbol.
            session (aiohttp.ClientSession, optional): Existing aiohttp session.

        Returns:
            dict: A dictionary with the ticker symbol as key and the fetched data or None.
        """

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize={self.outputsize}&datatype={self.datatype}&apikey={self.api_key}'

        if session is None:
            async with aiohttp.ClientSession() as new_session:
                async with self.semaphore:
                    async with new_session.get(url) as response:
                        if response.status == 200:


                            if self.datatype == "json":
                                json_data = await response.json()
                                print(json_data)
                                if "Time Series (Daily)" in json_data:
                                    return {ticker: json_data["Time Series (Daily)"]}
                                elif "Note" in json_data:
                                    print(f"[Rate Limit] API call limit hit: {json_data['Note']}")
                                elif "Error Message" in json_data:
                                    print(f"[Error] API Error: {json_data['Error Message']}")
                                else:
                                    print(f"[Error] Unexpected response: {json_data}")
                                return {ticker: None}




                            # if self.datatype == "json":
                            #     data = await response.json()
                            # else:
                            #     data = await response.text()
                            # return {ticker: data.get("Time Series (Daily)")}
                        return {ticker: None}
        else:
            async with self.semaphore:
                async with session.get(url) as response:
                    if response.status == 200:


                        if self.datatype == "json":
                            json_data = await response.json()
                            print(json_data)
                            if "Time Series (Daily)" in json_data:
                                return {ticker: json_data["Time Series (Daily)"]}
                            elif "Note" in json_data:
                                print(f"[Rate Limit] API call limit hit: {json_data['Note']}")
                            elif "Error Message" in json_data:
                                print(f"[Error] API Error: {json_data['Error Message']}")
                            else:
                                print(f"[Error] Unexpected response: {json_data}")
                            return {ticker: None}



                        # if self.datatype == "json":
                        #     data = await response.json()
                        #     return {ticker: data.get("Time Series (Daily)")}
                        # else:
                        #     data = await response.text()
                        #     return {ticker: data}
                    return {ticker: None}


async def fetch_single_adjdaily(ticker: str, outputsize: str = "compact", datatype: str = "json") -> dict:
    """
    Fetch news for a single ticker symbol.

    Args:
        ticker (str): Stock ticker.
        api_key (str): Alpha Vantage API key.
        outputsize (str): 'compact' for latest 100 points, 'full' for full history.
        datatype (str): 'json' or 'csv'.

    Returns:
        dict: Ticker -> daily adjusted price
    """
    fetcher = AlphaVantageHistPriceFetcher(api_keys["alphavantage"], outputsize, datatype)
    async with aiohttp.ClientSession() as session:
        return await fetcher.fetch_adjdaily(ticker, session=session)
    