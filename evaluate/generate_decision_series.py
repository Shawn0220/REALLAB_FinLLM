import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.fin_utils import get_position_list
from autogen import UserProxyAgent
from config.api_config import llm_config
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
import argparse


# === Parse Argument ===
parser = argparse.ArgumentParser()
parser.add_argument("--stock_name", type=str, required=True)
args = parser.parse_args()
stock_name = args.stock_name


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

DATES = ['2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
               '2024-01-08', '2024-01-09', '2024-01-10', '2024-01-11',
               '2024-01-12', '2024-01-16', '2024-01-17', '2024-01-18',
               '2024-01-19', '2024-01-22', '2024-01-23', '2024-01-24',
               '2024-01-25', '2024-01-26', '2024-01-29', '2024-01-30',
               '2024-01-31', '2024-02-01', '2024-02-02', '2024-02-05',
               '2024-02-06', '2024-02-07', '2024-02-08', '2024-02-09',
               '2024-02-12', '2024-02-13', '2024-02-14', '2024-02-15',
               '2024-02-16', '2024-02-20', '2024-02-21', '2024-02-22',
               '2024-02-23', '2024-02-26', '2024-02-27', '2024-02-28',
               '2024-02-29', '2024-03-01', '2024-03-04', '2024-03-05',
               '2024-03-06', '2024-03-07', '2024-03-08', '2024-03-11',
               '2024-03-12', '2024-03-13', '2024-03-14', '2024-03-15',
               '2024-03-18', '2024-03-19', '2024-03-20', '2024-03-21',
               '2024-03-22', '2024-03-25', '2024-03-26', '2024-03-27',
               '2024-03-28']

# DATES = ['2024-01-04', '2024-01-05']

# === Run ===

agents_outputs = []
manager_fail_times = 0
fail_contents = []

for date in DATES:
    agents_output, manager_fail, fail_content = run_stock_recommendation(
        stock_name, agents, user_proxy, debate_mgr, 
        risk_profile="Neutral", today_date=date
    )
    print("agents_output: ", agents_output)
    agents_outputs.append(agents_output)
    
    if manager_fail:
        manager_fail_times += 1
        fail_contents.append(fail_content)


position_list = get_position_list(agents_outputs)
print(position_list)
# === Save Results ===
out_dir = "results"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, f"{stock_name}.txt")
with open(out_path, "w") as f:
    f.write(",".join(map(str, position_list)) + "\n")

print("manager_fail_times", manager_fail_times)