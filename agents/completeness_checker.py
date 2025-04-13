from autogen import AssistantAgent

def get_completeness_check_agent(llm_config):
    return AssistantAgent(
        name="completeness_check_agent",
        llm_config=llm_config,
        system_message="""
        You are the checking manager_agent's decision
        if they give certain decision in EXECUTE_TRADE or DO_NOT_EXECUTE, reply:
        "FINISHED"
        """
    )