
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


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    import hmac
    import logging

    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not secret or not token:
        raise HTTPException(
            status_code=503,
            detail="Telegram integration not configured"
        )

    supplied = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token", ""
    )

    if not hmac.compare_digest(supplied, secret):
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook secret"
        )

    update_id = None
    claimed = False

    try:
        try:
            payload = await request.json()
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(
                status_code=400,
                detail='Invalid JSON payload'
            )

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Invalid Telegram payload")

        update_id = payload.get("update_id")

        if type(update_id) is not int:
            raise HTTPException(status_code=400, detail="Invalid update ID")

        if not update_tracker.claim(update_id):
            return {
                "ok": True,
                "processed": False,
                "duplicate": True
            }

        claimed = True

        routed = route_message(
            payload,
            bot_username="NexmindCybersafe_bot"
        )

        action = routed["action"]
        message = routed["message"]

        if action == "IGNORE":
            update_tracker.mark_processed(update_id)
            return {
                "ok": True,
                "processed": True,
                "ignored": True
            }

        chat_id = message.get("chat_id")
        text = message.get("text", "")

        if chat_id is None:
            update_tracker.mark_processed(update_id)
            return {
                "ok": True,
                "processed": True,
                "ignored": True
            }

        if action == "REPLY_HELP":
            reply = (
                "Welcome to NexMind CyberSafe AI!\n\n"
                "PRIVATE CHAT:\n"
                "Send or forward a suspicious text message.\n\n"
                "GROUP CHAT:\n"
                "Use /check followed by suspicious text.\n\n"
                "Commands: /start, /help, /check\n\n"
                "Never share passwords, PINs, BVNs, or OTPs."
            )

        elif action == "REPLY_APP":
            reply = (
                "CYBERSAFE AI — OPEN APP\\n\\n"
                "Open our Telegram bot using the link below:\\n"
                "https://t.me/NexmindCybersafe_bot\\n\\n"
                "Type /start and use the existing "
                "Mini App launch option."
            )

        elif action == "REPLY_USAGE":
            reply = (
                "Usage: /check followed by the suspicious message.\n"
                "Example: /check Your account will be blocked."
            )

        elif action == "REPLY_UNSUPPORTED_MEDIA":
            reply = (
                "I received your media message, but this version "
                "cannot analyze images, screenshots, audio, or "
                "documents directly. Please type or paste the "
                "suspicious text instead. Do not include passwords "
                "or other sensitive information."
            )

        elif action == "REPLY_UNKNOWN_COMMAND":
            reply = (
                "Unknown command. Use /help for instructions "
                "or send a suspicious message for analysis."
            )

        elif action == "ANALYZE":
            if not text.strip():
                reply = "Please provide a suspicious message to analyze."

            elif len(text) > 4000:
                reply = (
                    "Please send a message under 4000 characters."
                )

            else:
                state = await asyncio.to_thread(
                    cybersafe_graph.invoke,
                    {"message": text}
                )

                risk = state["risk_result"]

                reasons = "\n".join(
                    "- " + str(item)
                    for item in risk.get("reasons", [])
                ) or "No matching patterns identified."

                recommendations = "\n".join(
                    "- " + str(item)
                    for item in risk.get("recommendations", [])
                ) or "Verify suspicious claims through official channels."

                category_labels = {
                    "bank_fraud": "Banking fraud",
                    "credential_theft": "Credential theft",
                    "fake_job": "Fake recruitment",
                    "investment_scam": "Investment scam",
                    "grant_scam": "Grant or prize scam",
                    "account_takeover": "Account takeover",
                }

                categories = risk.get("threat_categories", [])

                category_text = "\n".join(
                    "- " + category_labels.get(
                        category,
                        category.replace("_", " ").title()
                    )
                    for category in categories
                ) or "No specific category identified."


                detection = state["detection_result"]

                ml_prediction = detection.get(
                    "ml_prediction", "Unavailable"
                )

                ml_confidence = detection.get(
                    "ml_confidence"
                )

                if ml_confidence is not None:
                    ml_confidence_text = (
                        f"{float(ml_confidence) * 100:.2f}%"
                    )
                else:
                    ml_confidence_text = "Unavailable"

                ml_section = (
                    "ML Model Analysis (Advisory)" + '\n'
                    + f"Predicted class: {ml_prediction}" + '\n'
                    + f"Model confidence: {ml_confidence_text}" + '\n'
                    + "This model was trained on phishing emails. "
                    + "Class meanings require confirmation from "
                    + "training records. Predictions are not "
                    + "verified threats." + '\n\n'
                )
                reply = (
                    "CYBERSAFE AI SECURITY REPORT\n\n"
                    f"Risk Level: {risk['risk_level']}\n"
                    f"Heuristic Score: "
                    f"{risk['heuristic_score']}/100\n\n"
                    f"{ml_section}"
                    f"Possible Threat Categories:\n"
                    f"{category_text}\n\n"
                    f"Reasons:\n{reasons}\n\n"
                    f"Recommended Actions:\n"
                    f"{recommendations}\n\n"
                    "External verification: Incomplete.\n"
                    "This is a preliminary assessment, "
                    "not a probability of fraud. "
                    "A low score does not establish safety."
                )

        else:
            update_tracker.mark_processed(update_id)
            return {
                "ok": True,
                "processed": True,
                "ignored": True
            }

        async with Bot(token=token) as bot:
            await bot.send_message(
                chat_id=chat_id,
                text=reply
            )

        update_tracker.mark_processed(update_id)

        return {
            "ok": True,
            "processed": True,
            "action": action
        }

    except HTTPException:
        raise
    except Exception:
        if claimed and type(update_id) is int:
            update_tracker.release(update_id)

        logging.exception(
            "CyberSafe AI webhook processing failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        )
