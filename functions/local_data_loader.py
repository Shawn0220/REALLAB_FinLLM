import os
import json

from datetime import datetime
from typing import Dict, Any

def safe_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def safe_int(x):
    try:
        return int(float(x))  # 有些数是 "123.0" 字符串
    except (TypeError, ValueError):
        return None


def fetch_single_adjdaily_locally(ticker: str) -> dict:
    """
    从本地加载单个股票的历史价格数据 JSON 文件。
    要求 JSON 格式为：{ "TICKER": { "YYYY-MM-DD": { ... }, ... } }
    
    Returns:
        dict: {ticker: {date: {...}, ...}}
    """
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, "..", "Data", "hist_price_jsons"))
    file_path = os.path.join(base_dir, f"{ticker}_hp.json")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Local data file not found for ticker: {ticker}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if ticker not in data:
        raise ValueError(f"Ticker {ticker} not found in the JSON file: {file_path}")

    return {ticker: data[ticker]}


def get_latest_report_before(reports: list, today: str) -> dict:
    filtered = [
        r for r in reports
        if "fiscalDateEnding" in r and r["fiscalDateEnding"] <= today
    ]
    if not filtered:
        return {}
    return sorted(filtered, key=lambda x: x["fiscalDateEnding"], reverse=True)[0]

def fetch_fundamental_summary(ticker: str, today: str) -> Dict[str, Any]:
    """
    加载指定股票的精简财务信息，只使用 today 之前的数据
    """
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, "..", "Data", "fundamental_jsons", ticker))

    def load_json(filename: str) -> dict:
        path = os.path.join(base_dir, filename)
        if not os.path.isfile(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    overview = load_json("OVERVIEW.json")
    income = load_json("INCOME_STATEMENT.json").get("annualReports", [])
    balance = load_json("BALANCE_SHEET.json").get("annualReports", [])
    cash = load_json("CASH_FLOW.json").get("annualReports", [])
    dividends = load_json("DIVIDENDS.json").get("data", [])
    earnings = load_json("EARNINGS.json").get("annualEarnings", [])

    income_report = get_latest_report_before(income, today)
    balance_report = get_latest_report_before(balance, today)
    cash_report = get_latest_report_before(cash, today)

    # EPS: 最近两条 fiscalDateEnding <= today
    eps_map = {
        e["fiscalDateEnding"]: safe_float(e["reportedEPS"])
        for e in earnings
        if e.get("fiscalDateEnding") and e.get("reportedEPS") not in ("None", None)
        and e["fiscalDateEnding"] <= today
    }
    top_eps_dates = sorted(eps_map.keys(), reverse=True)[:2]
    recent_eps = {d[:4]: eps_map[d] for d in top_eps_dates}

    # 最新的 ex_dividend_date <= today
    past_dividends = [
        d for d in dividends
        if d.get("ex_dividend_date") and d["ex_dividend_date"] <= today
    ]
    if past_dividends:
        latest_div = sorted(past_dividends, key=lambda x: x["ex_dividend_date"], reverse=True)[0]
        div_info = {
            "amount": safe_float(latest_div.get("amount")),
            "ex_date": latest_div.get("ex_dividend_date"),
            "pay_date": latest_div.get("payment_date")
        }
    else:
        div_info = {"amount": None, "ex_date": None, "pay_date": None}

    summary = {
        "symbol": ticker,
        "sector": overview.get("Sector"),
        "industry": overview.get("Industry"),
        "market_cap": safe_int(overview.get("MarketCapitalization")),
        "pe_ratio": safe_float(overview.get("PERatio")),
        "dividend_yield": safe_float(overview.get("DividendYield")),
        "eps": safe_float(overview.get("EPS")),
        "book_value": safe_float(overview.get("BookValue")),
        "analyst_target": safe_float(overview.get("AnalystTargetPrice")),

        "revenue": safe_int(income_report.get("totalRevenue")),
        "gross_profit": safe_int(income_report.get("grossProfit")),
        "operating_income": safe_int(income_report.get("operatingIncome")),
        "net_income": safe_int(income_report.get("netIncome")),
        "ebitda": safe_int(income_report.get("ebitda")),

        "total_assets": safe_int(balance_report.get("totalAssets")),
        "total_liabilities": safe_int(balance_report.get("totalLiabilities")),
        "cash": safe_int(balance_report.get("cashAndShortTermInvestments")),
        "long_term_debt": safe_int(balance_report.get("longTermDebt")),

        "operating_cashflow": safe_int(cash_report.get("operatingCashflow")),
        "capex": safe_int(cash_report.get("capitalExpenditures")),
        "dividend_payout": safe_int(cash_report.get("dividendPayout")),

        "last_dividend": div_info,
        "reported_eps": recent_eps
    }

    return summary


# print(load_fundamental_summary("TSLA", "2025-01-10"))

# print(load_fundamental_summary("WMB", "2025-01-10"))