# # User can edit this for custmized config
# agent_settings = {
#     "risk_profile": "Neutral", 
#     "enabled_tools": {
#         # "bearish_research_agent":["get_moving_average"],
#         # "bullish_research_agent": ["get_moving_average"],
#         # "calculator_agent": ["get_moving_average"],
#         # "analyst_agent": ["data_collect_company_info", "data_collect_stock_price_history", "data_collect_social_sentiment"],
#         "analyst_agent": ["get_stock_news_sentiment", "get_stock_price_history"],
#         # "analyst_agent": ["get_stock_price_history"],
#     }
# }


agent_settings = {
    "risk_profile": "Neutral",  # can be "Conservative", "Neutral", or "Aggressive"
    "enabled_tools": {
        "bullish_research_agent": [
            "moving_average",
            "macd",
            "trend_direction",
            "rsi",
            "support_resistance_levels",
            "candlestick_pattern_recognition"
        ],
        
        "bearish_research_agent": [
            "moving_average",
            "macd",
            "trend_direction",
            "rsi",
            "divergence_detection",
            "atr",
            "candlestick_pattern_recognition"
        ],
        
        "analyst_agent": [
            "get_stock_news_sentiment",
            "get_stock_price_history",
            "moving_average",
            "macd",
            "rsi"
        ],
        
        "calculator_agent": [
            "moving_average",
            "macd",
            "rsi",
            "atr"
        ]
    },
    
    "default_parameters": {
        "moving_average": {
            "window": 14,
            "ma_type": "simple",
            "price_type": "close"
        },
        "macd": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        },
        "rsi": {
            "period": 14
        },
        "atr": {
            "period": 14
        },
        "trend_direction": {
            "window": 20
        }
    }
}