import asyncio
import aiohttp
from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd
import json
import sys
target_path = str(Path(__file__).resolve().parents[1])
sys.path.append(target_path)
from alvan_dc.news_fetcher import AlphaVantageNewsFetcher

# Load API key from .env file
load_dotenv()
av_api = os.getenv("alphavantage_api_key")

# Define paths
parent_path = Path(__file__).resolve().parents[2]
data_path = parent_path / "Data"
output_dir_before2025 = data_path / "news_jsons" / "news_jsons_before2025"
output_dir_after2025 = data_path / "news_jsons" / "news_jsons_after2025"
output_dir_before2025.mkdir(parents=True, exist_ok=True)
output_dir_after2025.mkdir(parents=True, exist_ok=True)

# Load tickers
df_sp500_full = pd.read_csv(data_path / "sp500_list.csv", dtype={'CIK': str})
tickers = df_sp500_full['Symbol'].to_list()

# General fetch function
async def fetch_range(tickers, time_from, time_to, output_dir):
    fetcher = AlphaVantageNewsFetcher(
        api_key=av_api,
        time_from=time_from,
        time_to=time_to
    )

    async def fetch_and_save(ticker, session):
        result = await fetcher.fetch_news(ticker, session=session)
        for symbol, _ in result.items():
            output_file = output_dir / f"{symbol}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Saved {symbol}.json")

    batch_size = 75
    wait_time = 65

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} for {time_from} to {time_to}")
            tasks = [fetch_and_save(ticker, session) for ticker in batch]
            await asyncio.gather(*tasks)

            if i + batch_size < len(tickers):
                print(f"Sleeping {wait_time}s before next batch...")
                await asyncio.sleep(wait_time)

# Main entry
async def main():
    await fetch_range(tickers, "20240101T0130", "20241231T0130", output_dir_before2025)
    await fetch_range(tickers, "20250101T0000", "20251231T2359", output_dir_after2025)

if __name__ == "__main__":
    asyncio.run(main())
