
def extract_message(payload):
    """
    Extract and classify Telegram messages safely.
    This function does not contact Telegram or send messages.
    """

    if not isinstance(payload, dict):
        return {"status": "invalid", "reason": "Invalid update"}

    message = (
        payload.get("message")
        or payload.get("edited_message")
    )

    if not isinstance(message, dict):
        return {
            "status": "unsupported_update",
            "reason": "Unsupported Telegram update type"
        }

    chat = message.get("chat") or {}
    if not isinstance(chat, dict):
        chat = {}

    chat_id = chat.get("id")
    chat_type = chat.get("type", "unknown")

    if chat_id is None:
        return {
            "status": "invalid",
            "reason": "Missing chat ID"
        }

    text = message.get("text")
    caption = message.get("caption")

    if not isinstance(text, str):
        text = ""

    if not isinstance(caption, str):
        caption = ""

    content = text.strip() or caption.strip()

    is_forwarded = bool(
        message.get("forward_origin")
        or message.get("forward_date")
    )

    if content.startswith("/"):
        status = "command"

    elif content:
        status = "ready"

    elif message.get("photo"):
        status = "unsupported_media"

    elif message.get("document"):
        status = "unsupported_media"

    elif message.get("video"):
        status = "unsupported_media"

    elif message.get("voice") or message.get("audio"):
        status = "unsupported_media"

    else:
        status = "empty"

    return {
        "status": status,
        "chat_id": chat_id,
        "chat_type": chat_type,
        "message_id": message.get("message_id"),
        "text": content,
        "is_forwarded": is_forwarded,
        "has_photo": bool(message.get("photo")),
        "has_document": bool(message.get("document")),
        "reason": (
            "Media analysis is not yet supported."
            if status == "unsupported_media"
            else ""
        )
    }
