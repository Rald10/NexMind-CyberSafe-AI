🛡️ NexMind CyberSafe AI

Multi-Agent Cybersecurity Assistant for Phishing and Scam Detection

Developed by Team NexMind | Agentathon Project

CyberSafe AI is a Telegram-based cybersecurity assistant that helps users identify suspicious messages, potential phishing attempts, and online scams.

The system uses three specialized agents coordinated through LangGraph to analyze submitted messages and provide understandable security assessments and practical safety recommendations.

🚀 Live Application

Try CyberSafe AI on Telegram:

https://t.me/NexmindCybersafe_bot

Users can send or forward suspicious text messages directly to the bot without copying and pasting them into another application.

🎯 Problem Statement

Online scams, phishing attacks, financial fraud, and impersonation messages pose significant cybersecurity challenges, particularly for users with limited technical knowledge.

CyberSafe AI aims to make preliminary cybersecurity assessments accessible through a familiar messaging platform.

✨ Key Features

Automatic analysis of suspicious Telegram messages.

Support for forwarded text messages.

Three specialized cybersecurity agents.

LangGraph-based multi-agent orchestration.

Detection of urgency, sensitive-information requests, financial lures, and suspicious actions.

Preliminary offline inspection of URLs.

Heuristic risk classification: LOW, MEDIUM, and HIGH.

Explainable security reports with safety recommendations.

Telegram webhook integration.

Cloud deployment through Render.

🤖 Three-Agent Architecture

Agent 1 — Threat Detection

Examines incoming messages and identifies suspicious indicators, including urgency, requests for credentials, financial incentives, and potentially risky actions.

Output: Threat indicators and extracted URLs.

Agent 2 — Evidence Verification

Performs preliminary offline inspection of URLs and available indicators.

Output: Verification findings, warnings, and verification status.

External domain reputation and independent threat-intelligence verification are planned enhancements.

Agent 3 — Risk Assessment

Combines findings from the first two agents to produce a heuristic risk score, risk category, explanation, and safety recommendations.

Output: Final security assessment.

Workflow

Telegram User
     |
     v
Telegram Bot
     |
     v
FastAPI Webhook
     |
     v
LangGraph Orchestrator
     |
     v
Agent 1: Threat Detection
     |
     v
Agent 2: Evidence Verification
     |
     v
Agent 3: Risk Assessment
     |
     v
Security Report
     |
     v
Telegram User

🛠️ Technology Stack

Component

Technology

Programming language

Python

Agent orchestration

LangGraph

API framework

FastAPI

Server

Uvicorn

Messaging platform

Telegram Bot API

Database

SQLite

Development

Google Colab

Version control

GitHub

Cloud hosting

Render

📂 Project Structure

NexMind-CyberSafe-AI/
│
├── agents/
│   ├── __init__.py
│   ├── detection.py
│   ├── verification.py
│   └── risk_assessment.py
│
├── main.py
├── update_tracker.py
├── requirements.txt
├── render.yaml
├── .gitignore
└── README.md

⚙️ Installation

1. Clone the repository

git clone https://github.com/Rald10/NexMind-CyberSafe-AI.git
cd NexMind-CyberSafe-AI

Access to the repository is required if it is private.

2. Create a virtual environment

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

Or on Linux/macOS:

source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Set the following variables privately:

TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_WEBHOOK_SECRET=<your_webhook_secret>
CYBERSAFE_TRACKER_DB=telegram_updates.db

Never commit real credentials to GitHub.

5. Start the application

uvicorn main:app --host 0.0.0.0 --port 8000

Open:

http://localhost:8000/health

Expected response:

{
  "status": "ok",
  "service": "CyberSafe AI"
}

The Telegram webhook requires a publicly reachable HTTPS endpoint and registration through Telegram's Bot API.

📱 How to Use CyberSafe AI

Open https://t.me/NexmindCybersafe_bot.

Tap Start.

Send or forward a suspicious text message.

Wait for the security assessment.

Review the risk indicators and recommended precautions.

Example

Submitted message:

URGENT! Your bank account will be blocked. Click this link and send your OTP immediately.

Example assessment:

Risk level: HIGH

Heuristic score: 80/100

Indicators: urgency, sensitive-information request, suspicious action

Recommendation: Do not share your OTP or open suspicious links. Verify through official channels.

This example is illustrative; the result depends on the submitted message and implemented rules.

🔐 Security and Privacy

Telegram webhook requests are authenticated using a configured secret.

API credentials are stored outside source control.

Suspicious URLs are not automatically opened by the current verification agent.

Duplicate-update tracking is implemented using SQLite.

The bot analyzes messages deliberately submitted or forwarded by users.

Current limitations: Database persistence depends on the hosting environment, and the MVP does not guarantee exactly-once message delivery. Users should avoid submitting unnecessary sensitive personal information.

🧪 Testing and Evaluation

The MVP has undergone functional tests covering:

Individual agent execution.

LangGraph orchestration.

FastAPI health endpoint.

Telegram webhook handling.

Forwarded-message processing.

Sequential duplicate detection.

SQLite tracking across application reloads.

Live Telegram message responses.

These functional tests do not establish real-world phishing detection accuracy.

Future evaluation will include labeled Nigerian scam datasets, precision, recall, F1-score, false-positive rates, latency measurements, and agent ablation studies.

🗺️ Development Roadmap

Version 1.0 — Functional MVP

Three-agent architecture.

Telegram bot.

Forwarded-message analysis.

Heuristic risk assessment.

Render deployment.

Version 2.0 — Planned Improvements

Nigerian-specific scam categories.

External threat-intelligence verification.

Official-domain allowlists.

Improved reliability and persistent storage.

Telegram feedback and reporting commands.

English and Nigerian Pidgin support.

Expanded risk classifications.

Structured agent evaluation.

Future Research

Machine-learning and language-model detection.

Screenshot-based phishing analysis.

Multilingual cybersecurity assistance.

Comparative and ablation experiments.

👥 Team

Team NexMind

A five-member team developing accessible cybersecurity solutions using multi-agent technologies.

⚠️ Disclaimer

CyberSafe AI provides preliminary cybersecurity guidance and does not guarantee that a message, website, or sender is safe or fraudulent.

Users should independently verify suspicious claims through trusted official channels.

Developed by Team NexMind

Making cybersecurity guidance more accessible through multi-agent technology.
