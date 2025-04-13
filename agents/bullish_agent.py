from autogen import AssistantAgent

def get_bullish_agent(llm_config):
    return AssistantAgent(
        name="bullish_research_agent",
        llm_config=llm_config,
        system_message="""
        You are an optimistic stock researcher. Your job is to analyze data and argue why the stock is a good investment.
        You do not consider risks or negative sentiment. Your goal is to convince others the stock should be bought.
        """
    )