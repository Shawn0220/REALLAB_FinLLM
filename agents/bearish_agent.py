from autogen import AssistantAgent

def get_bearish_agent(llm_config):
    return AssistantAgent(
        name="bearish_research_agent",
        llm_config=llm_config,
        system_message="""
        You are a conservative stock researcher. Your job is to analyze data and argue why the stock is risky or not a good investment.
        Your goal is to point out why the stock should be avoided.
        """
    )
