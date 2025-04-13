from autogen import AssistantAgent

def get_spokesperson_agent(llm_config):
    return AssistantAgent(
        name="spokesperson_agent",
        llm_config=llm_config,
        system_message="""
        You are the spokesperson of the research team. Your job is to assess the trader's decision and evaluate whether it sufficiently considers the team's prior Bullish and Bearish arguments.
        
        If you think the trader's response reflects the team's views, say:
        "TERMINATE. Your decision reflects our team's analysis. You may stop here."

        Otherwise, ask for clarification or adjustment.
        """
    )