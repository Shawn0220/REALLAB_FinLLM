import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")
azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
azure_url = os.environ.get("AZURE_URL")

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
            "api_type": "azure",
            "api_key": azure_key,
            "base_url": azure_url,
            "api_version": "2025-01-01-preview",
        }
    ]
}