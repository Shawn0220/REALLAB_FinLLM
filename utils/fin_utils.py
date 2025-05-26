import re
import os
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta


def load_market_value_dict(ticker_list, folder_path=r"D:\shawn_workspace\REAL LAB\REALLAB_FinLLM\Data\market_cap", start="1900-01-01", end="2100-01-01"):
    """
    Load MarketCap values for selected tickers within a date range.

    Args:
        ticker_list (list): List of tickers, e.g., ["AAPL", "TSLA"]
        folder_path (str): Path to folder with CSV files
        start (str): Start date in "YYYY-MM-DD"
        end (str): End date in "YYYY-MM-DD"

    Returns:
        dict: {ticker: [market_cap1, market_cap2, ...]} within date range
    """
    market_value_dict = {}

    for ticker in ticker_list:
        file_path = os.path.join(folder_path, f"{ticker}.csv")
        try:
            df = pd.read_csv(file_path)
            if 'Date' not in df.columns or 'MarketCap' not in df.columns:
                print(f"Warning: Missing required columns in {ticker}.csv")
                continue

            # 转换Date列为datetime格式，并过滤时间区间
            df['Date'] = pd.to_datetime(df['Date'])
            df_filtered = df[(df['Date'] >= start) & (df['Date'] <= end)]

            # 提取MarketCap序列
            market_value_dict[ticker] = df_filtered['MarketCap'].tolist()

        except FileNotFoundError:
            print(f"File not found: {ticker}.csv")
        except Exception as e:
            print(f"Error processing {ticker}.csv: {e}")

    return market_value_dict

def evaluate_portfolio_performance(
    position_dict: dict,
    market_value_dict: dict,
    price_data_dict: dict,
    initial_cash: float = 10000.0
):
    """
    Evaluate portfolio performance with daily rebalancing based on position signals and market values.

    Args:
        position_dict (dict): {ticker: [0/1, 0/1, ...]} for each day
        market_value_dict (dict): {ticker: [mv1, mv2, ...]} for each day
        price_data_dict (dict): {ticker: pd.DataFrame with 'Open' and 'Close', index is datetime}
        initial_cash (float): Starting cash

    Returns:
        dict with:
            - daily_values: list of portfolio values per day
            - CR: cumulative return
            - AR: annualized return
    """
    tickers = position_dict.keys()
    n_days = len(next(iter(position_dict.values())))
    cash = initial_cash
    holdings = {ticker: 0.0 for ticker in tickers}
    daily_values = []
    previous_active_tickers = None
    change_portfolio = False

    for day_idx in range(n_days):
        print("\nnew day")
        active_tickers = [t for t in tickers if position_dict[t][day_idx] == 1]
        # 1. Sell all previous positions at today's open price
        # if  previous_active_tickers==active_tickers: 不用卖
        if not previous_active_tickers or previous_active_tickers != active_tickers: # 有变动，要买股票重组
            change_portfolio = True
            print("有变动")
            for ticker in tickers:
                if float(holdings[ticker]) > 0:
                    open_price = float(price_data_dict[ticker].iloc[day_idx]['Open'])
                    cash += holdings[ticker] * open_price
                    holdings[ticker] = 0.0
            print("变动前 卖掉所有 ", holdings)
        else:
            change_portfolio = False
        print("cash: ", cash)
        # 2. Determine which tickers to long today
        
        previous_active_tickers = active_tickers
        
        if active_tickers and change_portfolio:
            print("有股票要买")
            total_mv = sum(market_value_dict[t][day_idx] for t in active_tickers)

            for ticker in active_tickers:
                weight = market_value_dict[ticker][day_idx] / total_mv
                allocation = cash * weight
                open_price = float(price_data_dict[ticker].iloc[day_idx]['Open'])
                shares = allocation / open_price
                print(ticker," weight ",weight," allocation ",allocation, " shares", shares)
                holdings[ticker] = shares
            cash = 0.0  # all cash invested
            print("买完股票 ", holdings)

        # 3. At end of day, calculate portfolio value using close prices
        total_value = cash
        for ticker in tickers:
            if float(holdings[ticker]) > 0:
                close_price = float(price_data_dict[ticker].iloc[day_idx]['Close'])
                total_value += holdings[ticker] * close_price
        daily_values.append(total_value)
        print(holdings)


    # 4. Compute CR and AR
    CR = daily_values[-1] / initial_cash - 1
    AR = (1 + CR) ** (252 / n_days) - 1
    print("daily_values:", daily_values)
    return {
        "daily_values": daily_values,
        "CR": CR,
        "AR": AR
    }


def load_local_price_data(
    tickers: List[str],
    dir_path: str = r"D:\shawn_workspace\REAL LAB\REALLAB_FinLLM\Data\history_price_data",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Dict[str, pd.DataFrame]:
    price_data_dict = {}

    for ticker in tickers:
        file_path = os.path.join(dir_path, f"{ticker}.csv")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No file:{file_path}")

        df = pd.read_csv(file_path)

        df.columns = df.columns.str.strip().str.title()
        if "Date" not in df.columns:
            raise ValueError(f"{file_path} No 'Date' column")

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).set_index("Date")

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
            df = df[~df.index.isna()]

        if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
            df.index = df.index.tz_convert(None)

        if start:
            df = df.loc[df.index >= pd.to_datetime(start)]
        if end:
            df = df.loc[df.index <= pd.to_datetime(end)]


        keep_cols = ["Open", "High", "Low", "Close", "Volume"]
        df = df[[c for c in keep_cols if c in df.columns]]

        price_data_dict[ticker] = df

    return price_data_dict


def extract_trade_decisions(text: str):
    """
    Extract trader, risk manager, and manager decisions from the agent system output text.

    Returns:
        A dictionary with keys:
            - 'trader': 'BUY' or 'SELL'
            - 'risk': 'APPROVED' or 'REJECTED'
            - 'risk_tag': optional tag like 'Neutral' or None
            - 'manager': 'EXECUTE_TRADE' or 'DO_NOT_EXECUTE'
    """
    import re

    trader_match = re.search(r"\*\*(BUY|SELL)\*\*", text)
    risk_match = re.search(r"\b(APPROVED|REJECTED)\b(?:\s*\((\w+)\))?", text)
    manager_match = re.search(r"\*\*(EXECUTE_TRADE|DO_NOT_EXECUTE)\*\*", text)

    return {
        "trader": trader_match.group(1) if trader_match else None,
        "risk": risk_match.group(1) if risk_match else None,
        "risk_tag": risk_match.group(2) if risk_match and risk_match.lastindex >= 2 else None,
        "manager": manager_match.group(1) if manager_match else None,
    }


def get_position_list(agent_outputs: list[dict]) -> list[int]:
    """
    Given a list of agent decisions, return a list of 0/1 indicating holding status after each day.

    Args:
        agent_outputs (list[dict]): List of daily agent outputs. Each item must include:
            - 'date': str
            - 'trader': 'BUY' or 'SELL'
            - 'manager': 'EXECUTE_TRADE' or 'DO_NOT_EXECUTE'

    Returns:
        list[int]: 0 for no position (FLAT), 1 for holding (LONG), aligned with agent_outputs
    """
    position = 0  # 0: FLAT, 1: LONG
    position_list = []

    for output in agent_outputs:
        action = output["trader"]
        executed = output["manager"] == "EXECUTE_TRADE"

        if executed:
            if action == "BUY":
                position = 1
            elif action == "SELL":
                position = 0

        position_list.append(position)

    return position_list


def generate_trading_days(start, end):
    """
    Generate a list of trading days (YYYY-MM-DD) between start and end (inclusive).
    """
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    date_list = []
    curr = start_dt
    while curr <= end_dt:
        if curr.weekday() < 5:  # Weekdays only
            date_list.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
    return date_list


def run_portfolio_simulation(tickers, start, end, agents, user_proxy, debate_mgr, risk_profile="Neutral"):
    from orchestrator.stock_recommendation_workflow import run_stock_recommendation
    trading_days = generate_trading_days(start, end)
    
    # Step 1: Run agent decisions for each day and each stock
    position_dict = {ticker: [] for ticker in tickers}
    
    for date in trading_days:
        for ticker in tickers:
            decisions, _, _ = run_stock_recommendation(
                ticker, agents, user_proxy, debate_mgr, 
                risk_profile=risk_profile, today_date=date
            )
            position = get_position_list([decisions])[-1]  # Convert single day decision to 0/1
            position_dict[ticker].append(position)

    # Step 2: Load market cap and price data
    market_value_dict = load_market_value_dict(ticker_list=tickers, start=start, end=end)
    price_data_dict = load_local_price_data(tickers=tickers, start=start, end=end)


    print("position_dict: ", position_dict)
    # Step 3: Evaluate portfolio performance
    result = evaluate_portfolio_performance(
        position_dict=position_dict,
        market_value_dict=market_value_dict,
        price_data_dict=price_data_dict
    )

    return result