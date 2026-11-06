"""Offline smoke tests for NexMind CyberSafe AI upgrade.

Run from repository root: python test_upgrade_offline.py
No Telegram/Groq network calls, credentials, or production changes.
"""
import ast
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
for name in ('main.py', 'groq_integration.py', 'telegram_bot/message_router.py', 'telegram_bot/message_handler.py'):
    candidate = ROOT / name
    if not candidate.exists() and name.startswith('telegram_bot/'):
        candidate = ROOT / Path(name).name
    ast.parse(candidate.read_text(encoding='utf-8'))
print('PASS: Python syntax (4 files)')

# Support the staged download directory and final GitHub layout.
import sys
sys.path.insert(0, str(ROOT))
from telegram_bot.message_router import route_message

base = {'update_id': 123, 'message': {'chat': {'id': 999, 'type': 'private'}, 'photo': [{'file_id': 'small', 'file_size': 10}, {'file_id': 'large', 'file_size': 20}]}}
r = route_message(base, bot_username='NexmindCybersafe_bot')
assert r['action'] == 'ANALYZE_PHOTO' and r['message']['photo_file_id'] == 'large', r
print('PASS: Private photo routing')

forwarded = {'message': {'chat': {'id': 999, 'type': 'private'}, 'forward_origin': {'type': 'user'}, 'photo': [{'file_id': 'fwd'}]}}
r = route_message(forwarded, bot_username='NexmindCybersafe_bot')
assert r['action'] == 'ANALYZE_PHOTO' and r['message']['is_forwarded'], r
print('PASS: Forwarded photo routing')

group = {'message': {'chat': {'id': -10, 'type': 'supergroup'}, 'text': '/check', 'reply_to_message': {'photo': [{'file_id': 'replied'}]}}}
r = route_message(group, bot_username='NexmindCybersafe_bot')
assert r['action'] == 'ANALYZE_PHOTO' and r['message']['photo_file_id'] == 'replied', r
print('PASS: Group reply-to-photo routing')

plain = {'message': {'chat': {'id': 999, 'type': 'private'}, 'text': 'Urgent: verify your account'}}
r = route_message(plain, bot_username='NexmindCybersafe_bot')
assert r['action'] == 'ANALYZE', r
print('PASS: Existing text routing')

from groq_integration import analyze_text, extract_screenshot
class FakeMessage:
    content = 'Possible phishing: do not share passwords.'
class FakeChoice:
    message = FakeMessage()
class FakeResponse:
    model = 'test-model'
    choices = [FakeChoice()]
class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs['messages'][0]['role'] == 'system'
        return FakeResponse()
class FakeChat:
    completions = FakeCompletions()
class FakeClient:
    chat = FakeChat()
with patch('groq_integration._client', return_value=FakeClient()):
    result = analyze_text('Suspicious link', {'risk_level': 'HIGH', 'heuristic_score': 80})
    assert result['external_verification_complete'] is False
print('PASS: Mock Groq text analysis')

with patch('groq_integration._client', return_value=FakeClient()):
    try:
        extract_screenshot(b'not-an-image', 'image/jpeg')
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid image was accepted')
print('PASS: Invalid screenshot rejected')
print('OFFLINE SMOKE TESTS PASSED (not a live API or deployment test)')
