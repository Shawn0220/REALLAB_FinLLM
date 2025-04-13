from autogen import AssistantAgent

def get_recommender_agent(llm_config):
    return AssistantAgent(
        name="trade_recommender_agent",
        llm_config=llm_config,
        system_message="""
        You are the delivering Trader's decision to risk team
        whatever they say, just reply:
        "TERMINATE"
        """
    )