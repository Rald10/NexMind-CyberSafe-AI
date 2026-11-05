
from .message_handler import extract_message


def route_message(payload, bot_username=None):
    """
    Determine how CyberSafe AI should handle a Telegram update.

    This function does not send Telegram messages.
    """

    message = extract_message(payload)

    status = message.get("status")
    chat_type = message.get("chat_type")
    text = message.get("text", "")

    if status in ("invalid", "unsupported_update", "empty"):
        return {"action": "IGNORE", "message": message}

    is_group = chat_type in ("group", "supergroup")

    if status == "unsupported_media":
        return {
            "action": "IGNORE" if is_group else "REPLY_UNSUPPORTED_MEDIA",
            "message": message
        }

    first_word, _, remaining = text.partition(" ")
    first_word = first_word.strip()

    command = ""
    target = None

    if first_word.startswith("/"):
        command_part, _, target = first_word.partition("@")
        command = command_part.lower()

        if target and bot_username:
            if target.lower() != bot_username.lstrip("@").lower():
                return {"action": "IGNORE", "message": message}

        elif target and is_group:
            return {"action": "IGNORE", "message": message}

    raw_message = (
        payload.get("message")
        or payload.get("edited_message")
        or {}
    )

    replied = raw_message.get("reply_to_message") or {}

    replied_text = (
        replied.get("text")
        or replied.get("caption")
        or ""
    )

    if not isinstance(replied_text, str):
        replied_text = ""

    replied_text = replied_text.strip()

    if is_group:
        if command in ("/start", "/help"):
            action = "REPLY_HELP"

        elif command == "/app":
            action = "REPLY_APP"

        elif command == "/check":
            action = "ANALYZE" if (remaining.strip() or replied_text) else "REPLY_USAGE"

        else:
            action = "IGNORE"

    else:
        if command in ("/start", "/help"):
            action = "REPLY_HELP"

        elif command == "/app":
            action = "REPLY_APP"

        elif command == "/check":
            action = "ANALYZE" if (remaining.strip() or replied_text) else "REPLY_USAGE"

        elif status == "command":
            action = "REPLY_UNKNOWN_COMMAND"

        else:
            action = "ANALYZE"

    if action == "ANALYZE" and command == "/check":
        message["text"] = remaining.strip() or replied_text

    return {"action": action, "message": message}
