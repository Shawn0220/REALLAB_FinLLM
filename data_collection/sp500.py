import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
from pathlib import Path

parent_path = Path().resolve().parent
data_path = parent_path.joinpath('Data')
data_path.mkdir(parents=True, exist_ok=True)

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", {"id": "constituents"})

table_html = str(table)
table_io = StringIO(table_html)

df_sp500_full = pd.read_html(table_io)[0]

df_sp500_full['CIK'] = df_sp500_full['CIK'].astype(str).str.zfill(10)

save_path = data_path / "sp500_list.csv"
df_sp500_full.to_csv(save_path, index=False)

print(f"S&P 500 list saved to: {save_path}")
