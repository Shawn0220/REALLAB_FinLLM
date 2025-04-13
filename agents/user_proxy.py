from autogen import UserProxyAgent

def get_user_proxy():
    return UserProxyAgent(
        name="user_proxy_agent",
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
        code_execution_config={"use_docker": False}
    )