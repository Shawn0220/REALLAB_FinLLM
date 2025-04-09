from pathlib import Path
import json
from dotenv import load_dotenv
import os
from edgar import *
import pandas as pd

load_dotenv()
sec_id = os.getenv('sec_id')

parent_path = Path().resolve().parent
data_path = parent_path / "data"
output_dir = data_path / "company_sec_jsons"
output_dir.mkdir(exist_ok=True)

df_sp500_full = pd.read_csv(data_path / "sp500_list.csv", dtype={'CIK': str})

set_identity(sec_id)

for idx, row in df_sp500_full.iterrows(): 
    cik = row['CIK']
    ticker = row['Symbol']
    company_name = row['Security']
    company_sector = row['GICS Sector']

    try:
        company = Company(cik)
        fillings = company.get_filings(form=['10-K', '10-Q']).head(4)
    except Exception as e:
        print(f"Failed to get filings for {ticker}: {e}")
        continue

    filing_data = []

    for filing in fillings:
        filing_obj = filing.obj()
        form_type = filing_obj.form
        filing_date = str(filing_obj.filing_date)

        risk_factors = filing_obj['Item 1A'] if 'Item 1A' in filing_obj.items else "Not available"

        if form_type == "10-K":
            mdna = filing_obj['Item 7'] if 'Item 7' in filing_obj.items else "Not available"
            financials = filing_obj['Item 8'] if 'Item 8' in filing_obj.items else "Not available"
        elif form_type == "10-Q":
            mdna = filing_obj['Item 2'] if 'Item 2' in filing_obj.items else "Not available"
            financials = filing_obj['Item 1'] if 'Item 1' in filing_obj.items else "Not available"
        else:
            mdna = "Not available"
            financials = "Not available"

        filing_data.append({
            "form": form_type,
            "filing_date": filing_date,
            "risk_factors": risk_factors,
            "mdna": mdna,
            "financials": financials
        })

    company_record = {
        "cik": cik,
        "ticker": ticker,
        "company_name": company_name,
        "company_sector": company_sector,
        "filings": filing_data
    }

    filename = f"{ticker}_{cik}.json"
    save_path = output_dir / filename

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(company_record, f, indent=2, ensure_ascii=False)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Failed to save {filename}: {e}")



        

def get_company_filings(cik, n_filings=4):
    """
    Extract recent 10-K and 10-Q filings for a given company CIK.

    Args:
        cik (str): The CIK of the company.
        n_filings (int): Number of recent filings to fetch (default: 4).

    Returns:
        List[dict]: A list of filing information dictionaries.
    """
    try:
        company = Company(cik)
        filings = company.get_filings(form=['10-K', '10-Q']).head(n_filings)
    except Exception as e:
        print(f"Failed to get filings for {cik}: {e}")
        return []

    filing_data = []

    for filing in filings:
        try:
            filing_obj = filing.obj()
            form_type = filing_obj.form
            filing_date = str(filing_obj.filing_date)

            # Extract the needed sections
            risk_factors = filing_obj['Item 1A'] if 'Item 1A' in filing_obj.items else "Not available"
            if form_type == "10-K":
                mdna = filing_obj['Item 7'] if 'Item 7' in filing_obj.items else "Not available"
                financials = filing_obj['Item 8'] if 'Item 8' in filing_obj.items else "Not available"
            elif form_type == "10-Q":
                mdna = filing_obj['Item 2'] if 'Item 2' in filing_obj.items else "Not available"
                financials = filing_obj['Item 1'] if 'Item 1' in filing_obj.items else "Not available"
            else:
                mdna = "Not available"
                financials = "Not available"

            filing_data.append({
                "form": form_type,
                "filing_date": filing_date,
                "risk_factors": risk_factors,
                "mdna": mdna,
                "financials": financials
            })

        except Exception as e:
            print(f"Failed to process a filing for {cik}: {e}")
            continue

    return filing_data