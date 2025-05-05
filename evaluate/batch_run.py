import subprocess

stock_list = ['TSLA', 'AAPL']

for stock in stock_list:
    print(f"Running {stock}...")
    subprocess.run(["python", "generate_decision_series.py", "--stock_name", stock])
