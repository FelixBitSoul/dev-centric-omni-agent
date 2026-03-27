from langchain_core.messages import ToolMessage


def cleanup_tool_outputs(state):
    """Framework helper: convert list-style ToolMessage content to string."""
    messages = state["messages"]
    new_messages = []

    for msg in messages:
        if isinstance(msg, ToolMessage) and isinstance(msg.content, list):
            text_content = "\n".join([
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in msg.content
            ])
            msg = ToolMessage(
                content=text_content,
                tool_call_id=msg.tool_call_id,
                name=msg.name,
                additional_kwargs=msg.additional_kwargs,
                artifact=msg.artifact,
            )
        new_messages.append(msg)

    return {"messages": new_messages}
