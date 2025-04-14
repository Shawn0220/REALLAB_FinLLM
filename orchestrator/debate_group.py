from autogen import GroupChat, GroupChatManager

def create_debate_group(bullish_agent, bearish_agent, calculator_agent, summary_agent):
    group = GroupChat(
        agents=[bullish_agent, bearish_agent, calculator_agent, summary_agent],
        messages=[],
        max_round=10,
        speaker_selection_method="round_robin"
    )
    return GroupChatManager(groupchat=group)
