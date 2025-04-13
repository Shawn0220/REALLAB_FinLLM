from autogen import AssistantAgent, UserProxyAgent
from autogen import register_function
from typing import Callable

def register_tool(
    user_proxy: UserProxyAgent,
    agent: AssistantAgent,
    tool_func: Callable,
    tool_name: str,
    tool_description: str
) -> None:
    """
    Register a tool function for a single agent with a user proxy executor.

    Args:
        user_proxy (UserProxyAgent): The executor of the function.
        agent (AssistantAgent): The agent that can call the function.
        tool_func (Callable): The function to register.
        tool_name (str): The name exposed to the agent.
        tool_description (str): A human-readable description of the tool.
    """
    register_function(
        tool_func,
        caller=agent,
        executor=user_proxy,
        name=tool_name,
        description=tool_description
    )
