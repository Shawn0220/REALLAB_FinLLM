import asyncio
import aiohttp
from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd
import json
import sys

# Add project root
sys.path.append(str(Path(__file__).resolve().parents[1]))

from alvan_dc.ec_transcript_fetcher import AlphaVantageEarningCallFetcher

# Load API key
load_dotenv()
av_api = os.getenv("alphavantage_api_key")

# Paths
parent_path = Path(__file__).resolve().parents[2]
data_path = parent_path / "Data"
output_dir = data_path / "ec_transcripts_jsons"
output_dir.mkdir(parents=True, exist_ok=True)

# Load tickers
df_sp500_full = pd.read_csv(data_path / "sp500_list.csv", dtype={'CIK': str})
tickers = df_sp500_full['Symbol'].to_list()

# Example: last 8 quarters
quarters = [
    "2023Q1", "2023Q2", "2023Q3", "2023Q4",
    "2024Q1", "2024Q2", "2024Q3", "2024Q4",
    "2025Q1"
]

# Fetch logic
async def fetch_all_ec_transcripts(tickers, quarters, output_dir):
    fetcher = AlphaVantageEarningCallFetcher(api_key=av_api)

    async def fetch_and_save(ticker, quarter, session):
        ticker_dir = output_dir / ticker
        ticker_dir.mkdir(exist_ok=True)

        output_file = ticker_dir / f"{quarter}.json"
        if output_file.exists():
            print(f"[SKIP] {ticker} {quarter} already exists")
            return

        result = await fetcher.fetch_ec_transcript(ticker, quarter, session=session)
        if result:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] {ticker} {quarter}")
        else:
            print(f"[FAILED] {ticker} {quarter}")

    batch_size = 10 # 10*7
    wait_time = 65

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            print(f"\n Processing batch {i // batch_size + 1}")

            tasks = []
            for ticker in batch:
                for quarter in quarters:
                    tasks.append(fetch_and_save(ticker, quarter, session))

            await asyncio.gather(*tasks)

            if i + batch_size < len(tickers):
                print(f"Sleeping {wait_time}s to avoid rate limit...")
                await asyncio.sleep(wait_time)

# Entry
async def main():
    await fetch_all_ec_transcripts(tickers, quarters, output_dir)

if __name__ == "__main__":
    asyncio.run(main())
