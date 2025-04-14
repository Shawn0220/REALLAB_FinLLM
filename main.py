from autogen import UserProxyAgent
from config.llm_config import llm_config
from orchestrator.stock_recommendation_workflow import run_stock_recommendation
from orchestrator.debate_group import create_debate_group

from agents.analyst_agent import get_analyst_agent
from agents.bullish_agent import get_bullish_agent
from agents.bearish_agent import get_bearish_agent
from agents.trader_agent import get_trader_agent
from agents.spokesperson_agent import get_spokesperson_agent
from agents.recommender_agent import get_recommender_agent
from agents.risk_manager_agent import get_risk_manager_agent
from agents.manager_agent import get_manager_agent
from agents.completeness_checker import get_completeness_check_agent
from agents.calculator_agent import get_calculator_agent
from agents.summary_agent import get_summary_agent
from agents.user_proxy import get_user_proxy


from functions.tool_registration import register_tool
from functions.stock_data import *

# === Set up UserProxyAgent ===
user_proxy = get_user_proxy()

# === Initialize Agents ===
analyst = get_analyst_agent(llm_config)
bullish = get_bullish_agent(llm_config)
bearish = get_bearish_agent(llm_config)
trader = get_trader_agent(llm_config)
spokesperson = get_spokesperson_agent(llm_config)
recommender = get_recommender_agent(llm_config)
risk_manager = get_risk_manager_agent(llm_config)
manager = get_manager_agent(llm_config)
completeness_checker = get_completeness_check_agent(llm_config)
calculator_agent = get_calculator_agent(llm_config)
summary_agent = get_summary_agent(llm_config)

# === Tool registration ===
register_tool(user_proxy, analyst)
register_tool(calculator_agent, bullish)
register_tool(calculator_agent, bearish)

# === Setup Debate Group ===
debate_mgr = create_debate_group(bullish, bearish, calculator_agent, summary_agent)

# === Assemble Agent Dict ===
agents = {
    "analyst_agent": analyst,
    "bullish_agent": bullish,
    "bearish_agent": bearish,
    "trader_agent": trader,
    "spokesperson_agent": spokesperson,
    "trade_recommender_agent": recommender,
    "risk_manager_agent": risk_manager,
    "manager_agent": manager,
    "completeness_checker": completeness_checker
}

# === Run Recommendation Pipeline ===
if __name__ == "__main__":
    run_stock_recommendation("Tesla", agents, user_proxy, debate_mgr, risk_profile="Neutral")
