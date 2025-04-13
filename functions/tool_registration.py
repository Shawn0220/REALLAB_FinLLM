from config.agent_config import agent_settings
from autogen import register_function
from autogen import UserProxyAgent, AssistantAgent
from typing import Any
import inspect
import functions.stock_data as stock_data_module


def register_tool(user_proxy: UserProxyAgent, agent: AssistantAgent):
    """
    Registers all tools listed for the agent in agent_config, if the function exists in stock_data.py
    and contains _tool_config.
    """
    agent_name = agent.name
    enabled_tool_names = agent_settings.get("enabled_tools", {}).get(agent_name, [])

    for tool_name in enabled_tool_names:
        func = getattr(stock_data_module, tool_name, None)
        if func is None:
            print(f"[WARN] Function '{tool_name}' not found in stock_data.py.")
            continue
        if not hasattr(func, "_tool_config"):
            print(f"[WARN] Function '{tool_name}' lacks '_tool_config' metadata.")
            continue

        meta = func._tool_config
        register_function(
            func,
            caller=agent,
            executor=user_proxy,
            name=meta["name"],
            description=meta["description"]
        )
        print(f"[INFO] Registered '{tool_name}' for agent '{agent_name}'.")
