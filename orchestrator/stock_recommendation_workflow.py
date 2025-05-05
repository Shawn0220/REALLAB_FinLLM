from utils.message_utils import get_last_reply_from
from functions.stock_data import data_collect
import re
from utils.fin_utils import extract_trade_decisions

def run_stock_recommendation(
    stock_name: str,
    agents: dict,
    user_proxy,
    debate_manager,
    risk_profile: str,
    today_date: str
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
    analyst_prompt = f"Today is {today_date}. Please collect stock data for {stock_name}."
    user_proxy.initiate_chat(agents["analyst_agent"], message=analyst_prompt)

    # 获取 analyst 最后一条消息（即工具调用返回值）
    stock_data_response = get_last_reply_from(agents["analyst_agent"])
    # print("Raw analyst response:", stock_data_response)

    pass_data_to_analyze_prompt = "The following stock data is available:\n" + stock_data_response + "You are now in a team discussion. \nBullish researcher: explain why this stock is promising.\nBearish researcher: explain the risks and why it might not be a good investment.\nCalculator agent: focus on function call caculation and not giving any idea output.\nSummary agent: only work when neither of Bullish researcher/Bearish researcher has any further arguments, make summaries for both sides."
    pass_data_to_analyze_prompt = re.sub(r"(?i)terminate", "", pass_data_to_analyze_prompt)

    print("\n=== Step 2: Bullish vs Bearish Debate ===")
    user_proxy.initiate_chat(debate_manager, message=pass_data_to_analyze_prompt)

    debate_summary = "\n--- Debate Summary ---\n"
    for msg in debate_manager.groupchat.messages:
        if msg['name'] == "summary_agent":
            debate_summary += f"{msg['name']}: {msg['content']}\n"

    print("\n=== Step 3: Trader makes a decision ===")
    trader_prompt = (
        f"{pass_data_to_analyze_prompt}\n"
        f"{debate_summary}\n"
        "Based on the above, please make a BUY or SELL decision with reasoning.\n"
    )
    trader_prompt = re.sub(r"(?i)terminate", "", trader_prompt)

    agents["spokesperson_agent"].initiate_chat(agents["trader_agent"], message=trader_prompt)
    trader_decision = get_last_reply_from(agents["trader_agent"])

    print("Trader Decision:\n", trader_decision)

    print("\n=== Step 4: Risk Management Team reviews ===")
    risk_prompt = (
        f"{pass_data_to_analyze_prompt}\n\n"
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
        f"Trader's Decision:\n{trader_decision}\n\n"
        f"Risk Management Team's Decision:\n{risk_decision}\n\n"
        "Should we execute the trade?"
    )
    manager_prompt = re.sub(r"(?i)terminate", "", manager_prompt)



    hints = [
        "",  # 第一次不加任何提示
        "\n[Reminder: Respond with EXECUTE_TRADE or DO_NOT_EXECUTE and provide reasons.]",
        "\n[Your reply must begin with EXECUTE_TRADE or DO_NOT_EXECUTE.]",
        "\n[Please clearly state EXECUTE_TRADE or DO_NOT_EXECUTE at the beginning of your response.]",
        "\n[Format reminder: Response should contain EXECUTE_TRADE or DO_NOT_EXECUTE plus justification.]"
    ]

    max_retries = 5
    manager_agent_decision = None
    manager_fail = False
    fail_content = None

    for attempt in range(max_retries):
        try:
            hint = hints[attempt] if attempt < len(hints) else hints[-1]

            current_prompt = (
                f"Trader's Decision:\n{trader_decision}\n\n"
                f"Risk Management Team's Decision:\n{risk_decision}\n\n"
                "Should we execute the trade?" + hint
            )

            current_prompt = re.sub(r"(?i)terminate", "", current_prompt)

            agents["completeness_checker"].initiate_chat(agents["manager_agent"], message=current_prompt)
            manager_agent_decision = get_last_reply_from(agents["manager_agent"])

            if manager_agent_decision:
                break  # 成功就退出循环

        except Exception as e:
            print(f"[Retry {attempt + 1}/{max_retries}] Manager agent failed: {e}")
            
            # time.sleep(1)

    if manager_agent_decision is None:
        print("[Warning] Manager agent failed after retries. Using fallback.")
        manager_agent_decision = "DO_NOT_EXECUTE\nReason: Unable to determine due to repeated failures."
        manager_fail = True
        fail_content = trader_decision + risk_decision





    # agents["completeness_checker"].initiate_chat(agents["manager_agent"], message=manager_prompt)
    # manager_agent_decision = get_last_reply_from(agents["manager_agent"])
    # manager_agent_decision = "EXECUTE_TRADE"
         
    # print(trader_decision, '\n', risk_decision, '\n', manager_agent_decision, '\n')
    decision_text = trader_decision + risk_decision + manager_agent_decision
    decisions = extract_trade_decisions(decision_text)
    decisions["date"] = today_date
    print(decisions)
    return decisions, manager_fail, fail_content