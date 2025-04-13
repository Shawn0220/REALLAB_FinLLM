# User can edit this for custmized config
agent_settings = {
    "risk_profile": "Neutral", 
    "enabled_tools": {
        "risk_manager_agent": ["get_moving_average"],
        "analyst_agent": ["data_collect_company_info", "data_collect_stock_price_history", "data_collect_social_sentiment"],
    }
}