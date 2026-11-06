"""Parse Telegram updates without downloading media or calling external services.

Photo processing is enabled only after the message router and webhook are
updated. Do not merge this development file alone into production.
"""


def extract_message(payload):
    """Return normalized text and optional Telegram photo file identifier."""
    if not isinstance(payload, dict):
        return {"status": "invalid", "reason": "Invalid update"}

    message = payload.get("message") or payload.get("edited_message")
    if not isinstance(message, dict):
        return {"status": "unsupported_update", "reason": "Unsupported Telegram update type"}

    chat = message.get("chat") or {}
    if not isinstance(chat, dict):
        chat = {}
    chat_id = chat.get("id")
    if chat_id is None:
        return {"status": "invalid", "reason": "Missing chat ID"}

    text = message.get("text") if isinstance(message.get("text"), str) else ""
    caption = message.get("caption") if isinstance(message.get("caption"), str) else ""
    content = text.strip() or caption.strip()

    # Telegram sends photo sizes as a list; use the largest listed photo.
    photos = message.get("photo")
    photo_file_id = None
    if isinstance(photos, list):
        valid = [p for p in photos if isinstance(p, dict)
                 and isinstance(p.get("file_id"), str) and p["file_id"]]
        if valid:
            chosen = max(valid, key=lambda p: p.get("file_size", 0)
                         if isinstance(p.get("file_size", 0), int) else 0)
            photo_file_id = chosen["file_id"]

    if content.startswith("/"):
        status = "command"
    elif photo_file_id:
        status = "photo_ready"
    elif content:
        status = "ready"
    elif any(message.get(k) for k in ("document", "video", "voice", "audio", "photo")):
        status = "unsupported_media"
    else:
        status = "empty"

    return {
        "status": status,
        "chat_id": chat_id,
        "chat_type": chat.get("type", "unknown"),
        "message_id": message.get("message_id"),
        "text": content,
        "is_forwarded": bool(message.get("forward_origin") or message.get("forward_date")),
        "has_photo": bool(message.get("photo")),
        "photo_file_id": photo_file_id,
        "has_document": bool(message.get("document")),
        "reason": "Media analysis is not yet supported." if status == "unsupported_media" else "",
    }
