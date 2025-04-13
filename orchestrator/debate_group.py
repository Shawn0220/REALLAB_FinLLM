from autogen import GroupChat, GroupChatManager

def create_debate_group(bullish_agent, bearish_agent):
    group = GroupChat(
        agents=[bullish_agent, bearish_agent],
        messages=[],
        max_round=3,
        speaker_selection_method="round_robin"
    )
    return GroupChatManager(groupchat=group)
