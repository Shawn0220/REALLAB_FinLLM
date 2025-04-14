from autogen import AssistantAgent

def get_bullish_agent(llm_config):
    return AssistantAgent(
        name="bullish_research_agent",
        llm_config=llm_config,
        system_message="""
        You are an optimistic stock researcher. Your job is to analyze data and argue why the stock is a good investment.
        You are encouraged to use computational tools to support your arguments. You are not allowed to perform calculations yourself—delegate all computation tasks to the calculator_agent.
        Your goal is to convince others the stock should be bought. When you have no more arguments to offer, please make a declaration.
        """,
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
    )