
import asyncio
import aiohttp
from alvan_dc.news_fetcher import AlphaVantageNewsFetcher
from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd
import json

# Load API key from .env file
load_dotenv()
av_api = os.getenv("alphavantage_api_key")


parent_path = Path().resolve().parent
data_path = parent_path / "data"
output_dir = data_path / "news_jsons"
output_dir.mkdir(parents=True, exist_ok=True)

df_sp500_full = pd.read_csv(data_path / "sp500_list.csv", dtype={'CIK': str})

tickers = df_sp500_full['Symbol'].to_list()

fetcher = AlphaVantageNewsFetcher(
    api_key=av_api,
    time_from="20240101T0130",
    time_to="20250401T0130"
)

async def fetch_and_save(ticker, session):
    result = await fetcher.fetch_news(ticker, session=session)
    for symbol, _ in result.items():
        output_file = output_dir / f"{symbol}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved {symbol}.json")

async def main():
    batch_size = 75 
    wait_time = 65

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}")
            tasks = [fetch_and_save(ticker, session) for ticker in batch]
            print(f"Number of tasks:{len(tasks)}")
            await asyncio.gather(*tasks)

            if i + batch_size < len(tickers):
                print(f"Sleeping {wait_time}s before next batch...")
                await asyncio.sleep(wait_time)

if __name__ == "__main__":
    asyncio.run(main())
