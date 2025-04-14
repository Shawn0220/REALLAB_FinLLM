from autogen import AssistantAgent

def get_calculator_agent(llm_config):
    return AssistantAgent(
        name="calculator_agent",
        llm_config=llm_config,
        system_message="You are a tool executor. You are collaborating with bearish_agent and bullish_anget. Your job is to respond to explicit caculation tool calls. Do not give ideas.",
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
    )
