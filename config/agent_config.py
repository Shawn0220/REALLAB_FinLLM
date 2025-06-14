# User can edit this for custmized config
agent_settings = {
    "risk_profile": "Neutral", 
    "enabled_tools": {
        # "bearish_research_agent":["get_moving_average"],
        # "bullish_research_agent": ["get_moving_average"],
        # "calculator_agent": ["get_moving_average"],
        # "analyst_agent": ["data_collect_company_info", "data_collect_stock_price_history", "data_collect_social_sentiment"],
        "analyst_agent": ["get_stock_news_sentiment", "get_stock_price_history", "get_stock_fundamental_data"],
        # "analyst_agent": ["get_stock_price_history"],
    }
}