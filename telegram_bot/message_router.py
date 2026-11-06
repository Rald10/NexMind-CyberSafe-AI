"""Route Telegram updates for CyberSafe AI.

Photo routes are intentionally separate from text analysis: main.py must add
ANALYZE_PHOTO support before this branch is deployed. Do not merge alone.
"""

from .message_handler import extract_message


def route_message(payload, bot_username=None):
    """Return {'action': ..., 'message': ...} without side effects."""
    message = extract_message(payload)
    status = message.get('status')
    chat_type = message.get('chat_type')
    text = message.get('text', '')

    if status in ('invalid', 'unsupported_update', 'empty'):
        return {'action': 'IGNORE', 'message': message}

    is_group = chat_type in ('group', 'supergroup')
    if status == 'unsupported_media':
        return {'action': 'IGNORE' if is_group else 'REPLY_UNSUPPORTED_MEDIA', 'message': message}

    first_word, _, remaining = text.partition(' ')
    first_word = first_word.strip()
    command = ''
    target = None
    if first_word.startswith('/'):
        command_part, _, target = first_word.partition('@')
        command = command_part.lower()
        if target and bot_username and target.lower() != bot_username.lstrip('@').lower():
            return {'action': 'IGNORE', 'message': message}
        if target and is_group and not bot_username:
            return {'action': 'IGNORE', 'message': message}

    raw_message = payload.get('message') or payload.get('edited_message') or {}
    replied = raw_message.get('reply_to_message') or {}
    replied_text = replied.get('text') or replied.get('caption') or ''
    if not isinstance(replied_text, str):
        replied_text = ''
    replied_text = replied_text.strip()

    # Replying /check to a photo can request photo analysis without reposting it.
    replied_photos = replied.get('photo')
    replied_photo_id = None
    if isinstance(replied_photos, list):
        valid = [p for p in replied_photos if isinstance(p, dict) and isinstance(p.get('file_id'), str) and p['file_id']]
        if valid:
            replied_photo_id = max(valid, key=lambda p: p.get('file_size', 0) if isinstance(p.get('file_size', 0), int) else 0)['file_id']

    if is_group:
        if command in ('/start', '/help'):
            action = 'REPLY_HELP'
        elif command == '/app':
            action = 'REPLY_APP'
        elif command == '/check':
            if message.get('photo_file_id') or replied_photo_id:
                action = 'ANALYZE_PHOTO'
            else:
                action = 'ANALYZE' if (remaining.strip() or replied_text) else 'REPLY_USAGE'
        else:
            action = 'IGNORE'
    else:
        if command in ('/start', '/help'):
            action = 'REPLY_HELP'
        elif command == '/app':
            action = 'REPLY_APP'
        elif command == '/check':
            if message.get('photo_file_id') or replied_photo_id:
                action = 'ANALYZE_PHOTO'
            else:
                action = 'ANALYZE' if (remaining.strip() or replied_text) else 'REPLY_USAGE'
        elif status == 'command':
            action = 'REPLY_UNKNOWN_COMMAND'
        elif status == 'photo_ready':
            action = 'ANALYZE_PHOTO'
        else:
            action = 'ANALYZE'

    if command == '/check' and action in ('ANALYZE', 'ANALYZE_PHOTO'):
        message['text'] = remaining.strip() or replied_text
        if action == 'ANALYZE_PHOTO' and not message.get('photo_file_id'):
            message['photo_file_id'] = replied_photo_id
            message['has_photo'] = True

    return {'action': action, 'message': message}
