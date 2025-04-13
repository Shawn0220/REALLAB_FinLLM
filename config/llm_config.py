import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


llm_config = {
    "config_list": [
        {
            "model": "gpt-4",
            # "api_type": "azure",
            "api_key": OPENAI_API_KEY
            # "base_url": "https://hw2aiservices.openai.azure.com/",
            # "api_version": "2024-05-13",
        }
    ]
}

print(OPENAI_API_KEY)