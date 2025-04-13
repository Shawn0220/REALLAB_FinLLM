from autogen import AssistantAgent

def get_trader_agent(llm_config):
    return AssistantAgent(
        name="trader_agent",
        llm_config=llm_config,
        system_message="""
        You are a trader. You read the bullish and bearish arguments and make a BUY or SELL suggestion.
        Do NOT consider risk preference.
        Just focus on the quality of the arguments and market outlook.
        Output your recommendation as: BUY or SELL and a short justification.
        """,
        is_termination_msg=lambda msg: "terminate" in msg.get("content", "").lower()
    )