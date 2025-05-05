import pandas as pd

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
        # print("\nnew day")
        active_tickers = [t for t in tickers if position_dict[t][day_idx] == 1]
        # 1. Sell all previous positions at today's open price
        # if  previous_active_tickers==active_tickers: 
        if not previous_active_tickers or previous_active_tickers != active_tickers:
            change_portfolio = True

            for ticker in tickers:
                if float(holdings[ticker]) > 0:
                    open_price = float(price_data_dict[ticker].iloc[day_idx]['Open'])
                    cash += holdings[ticker] * open_price
                    holdings[ticker] = 0.0

        else:
            change_portfolio = False
        # print("cash: ", cash)
        # 2. Determine which tickers to long today
        
        previous_active_tickers = active_tickers
        
        if active_tickers and change_portfolio:

            total_mv = sum(market_value_dict[t][day_idx] for t in active_tickers)

            for ticker in active_tickers:
                weight = market_value_dict[ticker][day_idx] / total_mv
                allocation = cash * weight
                open_price = float(price_data_dict[ticker].iloc[day_idx]['Open'])
                shares = allocation / open_price
                # print(ticker," weight ",weight," allocation ",allocation, " shares", shares)
                holdings[ticker] = shares
            cash = 0.0  # all cash invested


        # 3. At end of day, calculate portfolio value using close prices
        total_value = cash
        for ticker in tickers:
            if float(holdings[ticker]) > 0:
                close_price = float(price_data_dict[ticker].iloc[day_idx]['Close'])
                total_value += holdings[ticker] * close_price
        daily_values.append(total_value)
        # print(holdings)


    # 4. Compute CR and AR
    CR = daily_values[-1] / initial_cash - 1
    AR = (1 + CR) ** (252 / n_days) - 1
    # print("daily_values:", daily_values)
    return {
        "daily_values": daily_values,
        "CR": CR,
        "AR": AR
    }

