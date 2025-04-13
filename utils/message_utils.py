def get_last_reply_from(cur_agent):
    # get cur_agent's last reply to others
    for msg_list in cur_agent.chat_messages.values():
        for msg in reversed(msg_list):
            if msg.get("role") == "assistant" and msg.get("name") == cur_agent.name:
                return msg["content"]
    return None