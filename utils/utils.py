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
