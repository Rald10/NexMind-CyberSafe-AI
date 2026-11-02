
import os
import asyncio
from typing import TypedDict

from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
from langgraph.graph import StateGraph, START, END

from agents.detection import ThreatDetectionAgent
from agents.verification import EvidenceVerificationAgent
from agents.risk_assessment import RiskAssessmentAgent

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
            state["verification_result"]
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

    try:
        payload = await request.json()

        update_id = (
            payload.get("update_id")
            if isinstance(payload, dict)
            else None
        )

        if not isinstance(update_id, int) or isinstance(update_id, bool):
            raise ValueError("Missing or invalid update_id")

        if not update_tracker.claim(update_id):
            return {
                "ok": True,
                "processed": False,
                "duplicate": True
            }


        if not isinstance(payload, dict):
            raise ValueError("Invalid update payload")

        message = payload.get("message") or {}

        if not isinstance(message, dict):
            return {"ok": True, "processed": False}

        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        text = message.get("text") or message.get("caption") or ""
        is_forwarded = bool(message.get("forward_origin"))

        if chat_id is None or not isinstance(text, str):
            return {"ok": True, "processed": False}

        if not text.strip():
            return {"ok": True, "processed": False}

        if text.startswith("/start"):
            reply = (
                "Welcome to NexMind CyberSafe AI!\n\n"
                "Send a suspicious message or link for analysis.\n"
                "Never share passwords, PINs, BVNs, or OTPs."
            )

        elif len(text) > 4000:
            reply = (
                "Please send a message under "
                "4000 characters."
            )

        else:
            state = await asyncio.to_thread(
                cybersafe_graph.invoke,
                {"message": text}
            )

            risk = state["risk_result"]

            reasons = "\n".join(
                "- " + item
                for item in risk["reasons"]
            ) or "No matching patterns identified."

            recommendations = "\n".join(
                "- " + item
                for item in risk["recommendations"]
            )

            reply = (
                "CYBERSAFE AI SECURITY REPORT\n\n"
                f"Risk Level: {risk['risk_level']}\n"
                f"Heuristic Score: "
                f"{risk['heuristic_score']}/100\n\n"
                f"Reasons:\n{reasons}\n\n"
                f"Recommendations:\n"
                f"{recommendations}\n\n"
                "External verification: Incomplete.\n"
                "This is a preliminary assessment, "
                "not a probability of fraud. "
                "A low score does not establish safety."
            )

        async with Bot(token=token) as bot:
            await bot.send_message(
                chat_id=chat_id,
                text=reply
            )

        update_tracker.mark_processed(update_id)

        return {"ok": True, "processed": True}

    except Exception:
        if "update_id" in locals() and type(update_id) is int:
            update_tracker.release(update_id)

        logging.exception(
            "CyberSafe AI webhook processing failed"
        )
        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        )
