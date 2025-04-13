from autogen import AssistantAgent

def get_manager_agent(llm_config):
    return AssistantAgent(
        name="manager_agent",
        llm_config=llm_config,
        system_message="""
        You are the manager. You make the final decision to execute the trade.
        Your output should include EXECUTE_TRADE or DO_NOT_EXECUTE and give reasons.
        """,
        is_termination_msg=lambda msg: "finished" in msg.get("content", "").lower()
    )