import asyncio
import aiohttp
from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd
import json
import sys

# Setup path
target_path = str(Path(__file__).resolve().parents[1])
sys.path.append(target_path)

from alvan_dc.fundamental_fetcher import AlphaVantageFundamentalFetcher

# Load API key
load_dotenv()
av_api = os.getenv("alphavantage_api_key")

# Paths
parent_path = Path(__file__).resolve().parents[2]
data_path = parent_path / "Data"
output_dir = data_path / "fundamental_jsons"
output_dir.mkdir(parents=True, exist_ok=True)

# Tickers
df_sp500_full = pd.read_csv(data_path / "sp500_list.csv", dtype={'CIK': str})
tickers = df_sp500_full['Symbol'].to_list()

# Fundamental data types
fundamentals = ["OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW", "EARNINGS", "DIVIDENDS"]

# Fetch Function
async def fetch_all_fundamentals(tickers, output_dir):
    fetcher = AlphaVantageFundamentalFetcher(api_key=av_api)

    async def fetch_and_save(ticker, func_name, session):
        output_ticker_dir = output_dir / ticker
        output_ticker_dir.mkdir(exist_ok=True)
        output_file = output_ticker_dir / f"{func_name}.json"

        if output_file.exists():
            print(f"[SKIP] {ticker} - {func_name} already exists")
            return

        result = await fetcher.fetch_fundamental(ticker, func_name, session=session)
        if result:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] {ticker} - {func_name}")
        else:
            print(f"[FAILED] {ticker} - {func_name}")

    batch_size = 12 # 12*6=72
    wait_time = 65

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            print(f"\n Processing batch {i // batch_size + 1}")

            tasks = []
            for ticker in batch:
                for func in fundamentals:
                    tasks.append(fetch_and_save(ticker, func, session))

            await asyncio.gather(*tasks)

            if i + batch_size < len(tickers):
                print(f"Sleeping {wait_time}s to avoid rate limit...")
                await asyncio.sleep(wait_time)

# Entry
async def main():
    await fetch_all_fundamentals(tickers, output_dir)

if __name__ == "__main__":
    asyncio.run(main())
