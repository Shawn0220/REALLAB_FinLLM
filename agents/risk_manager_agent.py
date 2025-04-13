from autogen import AssistantAgent
from config.agent_config import agent_settings

def get_risk_manager_agent(llm_config):
    risk_profile = agent_settings.get("risk_profile", "Neutral")

    return AssistantAgent(
        name="risk_manager_agent",
        llm_config=llm_config,
        system_message=f"""
        You are Risk Management Team. Current risk preference is: {risk_profile}.
        You evaluate trader's suggestion and tag it as Aggressive, Neutral, or Conservative.
        You can approve or reject the trade suggestion based on risk alignment.
        Only output one of these: APPROVED (with tag), or REJECTED (with reason).
        """,
        is_termination_msg=lambda msg: "terminate" in msg.get("content", "").lower()
    )
