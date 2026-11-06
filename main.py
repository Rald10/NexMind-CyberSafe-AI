
import os
import asyncio
from typing import TypedDict

from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
from langgraph.graph import StateGraph, START, END

from agents.detection import ThreatDetectionAgent
from agents.verification import EvidenceVerificationAgent
from agents.risk_assessment import RiskAssessmentAgent
from telegram_bot.message_router import route_message
from groq_integration import analyze_text, extract_screenshot, MAX_IMAGE_BYTES

app = FastAPI(title="NexMind CyberSafe AI")

detection_agent = ThreatDetectionAgent()
verification_agent = EvidenceVerificationAgent()
risk_agent = RiskAssessmentAgent()


class CyberSafeState(TypedDict, total=False):
    message: str
    detection_result: dict
    verification_result: dict
    risk_result: dict


def detect_threat(state: CyberSafeState):
    return {
        "detection_result": detection_agent.analyze(
            state["message"]
        )
    }


def verify_evidence(state: CyberSafeState):
    return {
        "verification_result": verification_agent.verify(
            state["detection_result"]
        )
    }


def assess_risk(state: CyberSafeState):
    return {
        "risk_result": risk_agent.assess(
            state["detection_result"],
            state["verification_result"],
            message=state['message']
)
    }


workflow = StateGraph(CyberSafeState)

workflow.add_node("detection", detect_threat)
workflow.add_node("verification", verify_evidence)
workflow.add_node("assessment", assess_risk)

workflow.add_edge(START, "detection")
workflow.add_edge("detection", "verification")
workflow.add_edge("verification", "assessment")
workflow.add_edge("assessment", END)

cybersafe_graph = workflow.compile()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CyberSafe AI"}




# CYBERSAFE_DUPLICATE_GUARD
import threading

_processed_update_ids = set()
_processing_update_ids = set()
_update_lock = threading.Lock()


# CYBERSAFE_SQLITE_INTEGRATION
from pathlib import Path
from update_tracker import UpdateTracker

TRACKER_DB_PATH = os.getenv(
    "CYBERSAFE_TRACKER_DB",
    str(Path(__file__).parent / "telegram_updates.db")
)

update_tracker = UpdateTracker(TRACKER_DB_PATH)


def _report(state):
    risk = state["risk_result"]
    detection = state["detection_result"]
    reasons = "\n".join("- " + str(x) for x in risk.get("reasons", [])) or "No matching patterns identified."
    recommendations = "\n".join("- " + str(x) for x in risk.get("recommendations", [])) or "Verify claims through official channels."
    labels = {
        "bank_fraud": "Banking fraud", "credential_theft": "Credential theft",
        "fake_job": "Fake recruitment", "investment_scam": "Investment scam",
        "grant_scam": "Grant or prize scam", "account_takeover": "Account takeover",
    }
    categories = "\n".join("- " + labels.get(x, str(x).replace("_", " ").title()) for x in risk.get("threat_categories", [])) or "No specific category identified."
    prediction = detection.get("ml_prediction")
    class_label = {0: "Safe / non-phishing", 1: "Phishing"}.get(prediction, str(prediction) if prediction is not None else "Unavailable")
    confidence = detection.get("ml_confidence")
    try:
        confidence_label = f"{float(confidence) * 100:.2f}%" if confidence is not None else "Unavailable"
    except (ValueError, TypeError):
        confidence_label = "Unavailable"
    return (
        "CYBERSAFE AI SECURITY REPORT\n\n"
        f"Risk Level: {risk.get('risk_level', 'Unknown')}\n"
        f"Heuristic Score: {risk.get('heuristic_score', 'Unavailable')}/100\n\n"
        f"ML Model Analysis (Advisory)\nPredicted class: {class_label}\n"
        f"Model confidence: {confidence_label}\n"
        "The classifier was trained on phishing emails; predictions are not verified threats.\n\n"
        f"Possible Threat Categories:\n{categories}\n\n"
        f"Reasons:\n{reasons}\n\n"
        f"Recommended Actions:\n{recommendations}\n\n"
        "External verification: Incomplete. This is a preliminary assessment, "
        "not a probability of fraud. A low score does not establish safety."
    )


def _groq_commentary(text, state):
    # Never override the authoritative local risk score or ML classification.
    risk = state["risk_result"]
    return analyze_text(text, {
        "risk_level": risk.get("risk_level"),
        "heuristic_score": risk.get("heuristic_score"),
        "reasons": risk.get("reasons", []),
        "threat_categories": risk.get("threat_categories", []),
    })["explanation"]


async def _analyze_message(text):
    state = await asyncio.to_thread(cybersafe_graph.invoke, {"message": text})
    reply = _report(state)
    if os.getenv("GROQ_API_KEY"):
        try:
            import logging
            commentary = await asyncio.wait_for(
                asyncio.to_thread(_groq_commentary, text, state), timeout=35
            )
            if commentary:
                reply += "\n\nGroq Contextual Guidance (Advisory):\n" + commentary[:1600]
        except Exception:
            logging.exception("Optional Groq text analysis failed; local report retained")
    return reply[:3900]


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    import hmac
    import logging

    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not secret or not token:
        raise HTTPException(status_code=503, detail="Telegram integration not configured")
    supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not hmac.compare_digest(supplied, secret):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    update_id = None
    claimed = False
    try:
        try:
            payload = await request.json()
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        if not isinstance(payload, dict) or type(payload.get("update_id")) is not int:
            raise HTTPException(status_code=400, detail="Invalid Telegram payload/update ID")
        update_id = payload["update_id"]
        if not update_tracker.claim(update_id):
            return {"ok": True, "processed": False, "duplicate": True}
        claimed = True
        routed = route_message(payload, bot_username="NexmindCybersafe_bot")
        action, message = routed["action"], routed["message"]
        chat_id = message.get("chat_id")
        if action == "IGNORE" or chat_id is None:
            update_tracker.mark_processed(update_id)
            return {"ok": True, "processed": True, "ignored": True}
        text = message.get("text", "")

        if action == "REPLY_HELP":
            reply = (
                "Welcome to NexMind CyberSafe AI!\n\n"
                "PRIVATE CHAT: Send suspicious text or a screenshot.\n"
                "GROUP CHAT: Use /check followed by text, or reply /check to a photo.\n"
                "Commands: /start, /help, /check, /app\n"
                "Screenshots are processed by an external AI provider when enabled. "
                "Do not send passwords, PINs, BVNs, OTPs, or private documents."
            )
        elif action == "REPLY_APP":
            reply = (
                "CYBERSAFE AI — OPEN APP\n\n"
                "https://t.me/NexmindCybersafe_bot\n\n"
                "Type /start and use the existing Mini App launch option."
            )
        elif action == "REPLY_USAGE":
            reply = "Usage: /check Your account will be blocked. Or reply /check to a screenshot."
        elif action == "REPLY_UNSUPPORTED_MEDIA":
            reply = (
                "I can analyze text and Telegram photos, but not documents, "
                "audio, or video. Please send a screenshot as a photo or paste the text. "
                "Do not include passwords or other secrets."
            )
        elif action == "REPLY_UNKNOWN_COMMAND":
            reply = "Unknown command. Use /help or send a suspicious message."
        elif action == "ANALYZE":
            if not isinstance(text, str) or not text.strip():
                reply = "Please provide a suspicious message to analyze."
            elif len(text) > 4000:
                reply = "Please send a message under 4000 characters."
            else:
                reply = await _analyze_message(text)
        elif action == "ANALYZE_PHOTO":
            photo_file_id = message.get("photo_file_id")
            if not photo_file_id:
                reply = "I could not locate the screenshot. Please resend it as a Telegram photo."
            elif not os.getenv("GROQ_API_KEY"):
                reply = "Screenshot analysis is temporarily unavailable. Please paste the suspicious text instead."
            else:
                try:
                    # Telegram get_file and download are restricted to the authenticated bot.
                    async with Bot(token=token) as bot:
                        tg_file = await bot.get_file(photo_file_id)
                        if tg_file.file_size and tg_file.file_size > MAX_IMAGE_BYTES:
                            raise ValueError("Image exceeds the 4 MB limit")
                        data = bytes(await tg_file.download_as_bytearray())
                    if len(data) > MAX_IMAGE_BYTES:
                        raise ValueError("Image exceeds the 4 MB limit")
                    if data.startswith(b"\xff\xd8\xff"):
                        mime = "image/jpeg"
                    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
                        mime = "image/png"
                    else:
                        raise ValueError("Only JPEG and PNG images are supported")
                    vision = await asyncio.wait_for(
                        asyncio.to_thread(extract_screenshot, data, mime), timeout=35
                    )
                    extracted = vision.get("extracted_text", "").strip()
                    if not vision.get("image_readable") or not extracted:
                        reply = "I could not reliably read this screenshot. Please paste its suspicious text instead."
                    else:
                        # Image extraction is untrusted; classify only extracted text.
                        reply = "SCREENSHOT ANALYSIS (AI-extracted text; verify against image)\n\n"
                        reply += await _analyze_message(extracted[:4000])
                        if vision.get("limitations"):
                            reply += "\n\nVision limitations: " + "; ".join(map(str, vision["limitations"]))[:350]
                except ValueError as exc:
                    reply = f"Screenshot not processed: {exc}. Please send a smaller JPEG/PNG photo or paste text."
                except Exception:
                    logging.exception("Screenshot analysis unavailable")
                    reply = "Screenshot analysis is temporarily unavailable. Please paste the suspicious text instead."
        else:
            update_tracker.mark_processed(update_id)
            return {"ok": True, "processed": True, "ignored": True}

        async with Bot(token=token) as bot:
            await bot.send_message(chat_id=chat_id, text=reply[:3900])
        update_tracker.mark_processed(update_id)
        return {"ok": True, "processed": True, "action": action}
    except HTTPException:
        if claimed and type(update_id) is int:
            update_tracker.release(update_id)
        raise
    except Exception:
        if claimed and type(update_id) is int:
            update_tracker.release(update_id)
        logging.exception("CyberSafe AI webhook processing failed")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
