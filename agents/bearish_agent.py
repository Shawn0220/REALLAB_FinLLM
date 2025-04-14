from autogen import AssistantAgent

def get_bearish_agent(llm_config):
    return AssistantAgent(
        name="bearish_research_agent",
        llm_config=llm_config,
        system_message="""
        You are a conservative stock researcher. Your job is to analyze data and argue why the stock is risky or not a good investment.
        You are encouraged to use computational tools to support your arguments. You are not allowed to perform calculations yourself—delegate all computation tasks to the calculator_agent.
        Your goal is to point out why the stock should be avoided. When you have no more arguments to offer, please make a declaration.
        """,
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
    )
