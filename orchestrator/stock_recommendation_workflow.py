from utils.message_utils import get_last_reply_from
from functions.stock_data import data_collect
import re

def run_stock_recommendation(
    stock_name: str,
    agents: dict,
    user_proxy,
    debate_manager,
    risk_profile: str
) -> None:
    """
    Orchestrates the stock recommendation pipeline.

    Args:
        stock_name (str): The target stock name.
        agents (dict): Dictionary of all agents.
        user_proxy: The UserProxyAgent that handles function execution.
        debate_manager: GroupChatManager for bullish/bearish debate.
        risk_profile (str): The user's risk preference (e.g., 'Neutral').
    """
    print("\n=== Step 1: Analyst collects data ===")
    analyst_prompt = f"Please collect stock data for {stock_name}."
    user_proxy.initiate_chat(agents["analyst_agent"], message=analyst_prompt)

    # 获取 analyst 最后一条消息（即工具调用返回值）
    stock_data_response = get_last_reply_from(agents["analyst_agent"])
    print("Raw analyst response:", stock_data_response)

    stock_data_str = stock_data_response

    print("\n=== Step 2: Bullish vs Bearish Debate ===")
    user_proxy.initiate_chat(debate_manager, message=f"The following stock data is available:\n{stock_data_str}")

    debate_summary = "\n--- Debate Summary ---\n"
    for msg in debate_manager.groupchat.messages:
        debate_summary += f"{msg['name']}: {msg['content']}\n"

    print("\n=== Step 3: Trader makes a decision ===")
    trader_prompt = (
        f"{stock_data_str}\n"
        f"{debate_summary}\n"
        "Based on the above, please make a BUY or SELL decision with reasoning.\n"
    )
    trader_prompt = re.sub(r"(?i)terminate", "", trader_prompt)

    agents["spokesperson_agent"].initiate_chat(agents["trader_agent"], message=trader_prompt)
    trader_decision = get_last_reply_from(agents["trader_agent"])

    print("Trader Decision:\n", trader_decision)

    print("\n=== Step 4: Risk Management Team reviews ===")
    risk_prompt = (
        f"{stock_data_str}\n\n"
        f"{debate_summary}\n"
        f"Trader's Decision:\n{trader_decision}\n\n"
        f"Current Risk Profile: {risk_profile}\n"
        "Evaluate if this decision aligns with risk preferences. Approve or reject."
    )
    risk_prompt = re.sub(r"(?i)terminate", "", risk_prompt)

    agents["trade_recommender_agent"].initiate_chat(agents["risk_manager_agent"], message=risk_prompt)
    risk_decision = get_last_reply_from(agents["risk_manager_agent"])
    print("Risk Manager Decision:\n", risk_decision)

    print("\n=== Step 5: Manager makes final decision ===")
    manager_prompt = (
        f"{stock_data_str}\n\n"
        f"{debate_summary}\n"
        f"Trader's Decision:\n{trader_decision}\n\n"
        f"Risk Management Team's Decision:\n{risk_decision}\n\n"
        "Should we execute the trade?"
    )
    manager_prompt = re.sub(r"(?i)terminate", "", manager_prompt)
    
    agents["completeness_checker"].initiate_chat(agents["manager_agent"], message=manager_prompt)
