import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")

MAX_articles = 10

# print(OPENAI_API_KEY)
api_keys = {
    "openai": OPENAI_API_KEY,
    "alphavantage": ALPHAVANTAGE_API_KEY
}


llm_config = {
    "config_list": [
        {
            "model": "gpt-4o",
            # "api_type": "azure",
            "api_key": api_keys["openai"]
            # "base_url": "https://hw2aiservices.openai.azure.com/",
            # "api_version": "2024-05-13",
        }
    ]
}