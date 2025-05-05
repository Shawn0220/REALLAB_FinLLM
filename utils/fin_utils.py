import re

def extract_trade_decisions(text: str):
    """
    Extract trader, risk manager, and manager decisions from the agent system output text.

    Returns:
        A dictionary with keys:
            - 'trader': 'BUY' or 'SELL'
            - 'risk': 'APPROVED' or 'REJECTED'
            - 'risk_tag': optional tag like 'Neutral' or None
            - 'manager': 'EXECUTE_TRADE' or 'DO_NOT_EXECUTE'
    """
    import re

    trader_match = re.search(r"\*\*(BUY|SELL)\*\*", text)
    risk_match = re.search(r"\b(APPROVED|REJECTED)\b(?:\s*\((\w+)\))?", text)
    manager_match = re.search(r"\*\*(EXECUTE_TRADE|DO_NOT_EXECUTE)\*\*", text)

    return {
        "trader": trader_match.group(1) if trader_match else None,
        "risk": risk_match.group(1) if risk_match else None,
        "risk_tag": risk_match.group(2) if risk_match and risk_match.lastindex >= 2 else None,
        "manager": manager_match.group(1) if manager_match else None,
    }


def get_position_list(agent_outputs: list[dict]) -> list[int]:
    """
    Given a list of agent decisions, return a list of 0/1 indicating holding status after each day.

    Args:
        agent_outputs (list[dict]): List of daily agent outputs. Each item must include:
            - 'date': str
            - 'trader': 'BUY' or 'SELL'
            - 'manager': 'EXECUTE_TRADE' or 'DO_NOT_EXECUTE'

    Returns:
        list[int]: 0 for no position (FLAT), 1 for holding (LONG), aligned with agent_outputs
    """
    position = 0  # 0: FLAT, 1: LONG
    position_list = []
    print(agent_outputs)
    for output in agent_outputs:
        action = output["trader"]
        executed = output["manager"] == "EXECUTE_TRADE"

        if executed:
            if action == "BUY":
                position = 1
            elif action == "SELL":
                position = 0

        position_list.append(position)

    return position_list
