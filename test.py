# {'ticker': 'GOOGL', 'time_from': '2023-01-01T0000', 'time_to': '2024-01-09T0000', 'sort': 'RELEVANCE'}
import asyncio
from data_collection.alvan_dc.news_fetcher import fetch_single_news
from functions.stock_data import normalize_time_string
# {"ticker":"GOOGL","time_from":"2023-12-01T00:00","time_to":"2024-01-04T23:59","sort":"RELEVANCE"} , , 'time_to': 
time_from = '2023-12-01T0000'
time_to = '2024-01-02T2359'
time_from = normalize_time_string(time_from)
time_to = normalize_time_string(time_to)
print(time_from, "*******", time_to)
full_result = asyncio.run(fetch_single_news("A", time_from= time_from, time_to=time_to))

print(full_result)