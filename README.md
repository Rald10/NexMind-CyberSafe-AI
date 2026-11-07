
# 🛡️ NexMind CyberSafe AI

### AI-Powered Cybersecurity Threat Detection and Awareness Assistant

**Developed by Team NexMind | Agentathon Project**

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)](https://t.me/NexmindCybersafe_bot)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?logo=render)](https://nexmind-cybersafe-ai.onrender.com)

**[Try CyberSafe AI on Telegram](https://t.me/NexmindCybersafe_bot)** | **[GitHub Repository](https://github.com/Rald10/NexMind-CyberSafe-AI)**

---

## 📖 Overview

**CyberSafe AI** is a Telegram-based cybersecurity assistant developed by **Team NexMind** to help users identify potentially harmful messages, phishing attempts, credential theft, and suspicious online activities.

The system combines:

- Machine learning-based phishing classification.
- Rule-based cybersecurity threat detection.
- Three specialized AI workflow agents.
- LangGraph orchestration.
- Heuristic risk scoring.
- Automated cybersecurity guidance.
- Telegram bot integration.

CyberSafe AI provides preliminary cybersecurity assessments and practical safety guidance.

---

## 🎯 Project Objectives

1. Analyze suspicious messages for cybersecurity threats.
2. Identify phishing-related indicators using machine learning.
3. Detect suspicious requests for OTPs, passwords, PINs, and sensitive information.
4. Evaluate threat severity using heuristic risk scores.
5. Provide understandable explanations of cybersecurity risks.
6. Deliver automated cybersecurity reports through Telegram.
7. Coordinate threat analysis using a multi-agent workflow.

---

## ✨ Implemented Features

### 1. Suspicious Message Analysis

CyberSafe AI analyzes text messages for:

- Urgency and psychological pressure.
- Requests for sensitive information.
- Suspicious instructions.
- Financial and investment scam indicators.
- Credential theft attempts.
- Suspicious URL characteristics.

### 2. Machine Learning Phishing Detection

CyberSafe AI includes a trained phishing detection classifier.

| Component | Implementation |
|---|---|
| Algorithm | Logistic Regression |
| Feature extraction | Hybrid word and character TF-IDF |
| Training dataset | 17,515 cleaned phishing email records |
| Classification | Binary |
| Class 0 | Non-phishing |
| Class 1 | Phishing |
| Decision threshold | 0.50 |
| Model persistence | Joblib |

The trained classifier is preserved and loaded for inference without retraining.

Model confidence is not a verified probability of fraud.

### 3. Three-Agent Cybersecurity Architecture

**Agent 1 — Threat Detection**

Analyzes messages for phishing indicators, suspicious actions, urgency, and requests for sensitive information.

**Agent 2 — Evidence Verification**

Performs preliminary offline checks, including suspicious URL analysis.

**Agent 3 — Risk Assessment**

Combines detection results into a structured report containing risk classification, supporting reasons, and security recommendations.

### 4. Risk Assessment

The system generates:

- Heuristic risk scores from 0 to 100.
- LOW, MEDIUM, and HIGH risk classifications.
- Possible threat categories.
- Reasons supporting the assessment.
- Recommended cybersecurity actions.

### 5. Telegram Bot

The operational Telegram bot supports:

- Direct text messages.
- Forwarded text messages.
- Automated cybersecurity analysis.
- Phishing classification.
- Structured security reports.
- Webhook-based communication.
- Duplicate-update protection.

**Telegram Bot:** [@NexmindCybersafe_bot](https://t.me/NexmindCybersafe_bot)

---

## 🏗️ System Architecture

```text
                 TELEGRAM USER
                       |
                       v
                TELEGRAM BOT API
                       |
                       v
                 FASTAPI WEBHOOK
                       |
                       v
               MESSAGE PROCESSING
                       |
                       v
              LANGGRAPH WORKFLOW
                       |
          +------------+------------+
          |            |            |
          v            v            v
       AGENT 1      AGENT 2      AGENT 3
       Threat       Evidence     Risk
       Detection    Verification Assessment
          |            |            |
          +------------+------------+
                       |
                       v
             CYBERSECURITY REPORT
                       |
                       v
                 TELEGRAM USER
```

---

## 🧪 Groq LLM and Vision Integration

CyberSafe AI includes Groq integration code developed and tested in Google Colab.

### Groq Text Analysis

The development implementation uses `openai/gpt-oss-20b` for contextual cybersecurity explanations.

### Groq Vision Analysis

The development implementation includes:

- Screenshot text extraction.
- Identification of suspicious message indicators.
- Structured extraction of cybersecurity evidence.
- Integration with the phishing classifier.

A recorded Colab screenshot experiment produced a **93.46% phishing-class probability**.

### Production Integration Status

Groq integration code was merged into the production repository through **Pull Request #2** and deployed successfully on Render.

At the latest confirmed check, the required `GROQ_API_KEY` was missing from the Render environment.

Therefore, live Groq contextual explanations and Telegram screenshot analysis have not yet been confirmed operational.

---

## 📱 Example CyberSafe AI Security Report

```text
CYBERSAFE AI SECURITY REPORT

Risk Level: MEDIUM
Heuristic Score: 55/100

ML Model Analysis (Advisory)
Predicted class: 1
Model confidence: 92.50%

Possible Threat Categories:
- Credential theft

Reasons:
- Message mentions sensitive credentials
- Message uses urgency or pressure

Recommended Actions:
- Never share OTPs, PINs or passwords.
- Change compromised credentials.
- Independently verify urgent requests.

External verification: Incomplete.
```

The assessment is preliminary and does not establish that a message is definitively fraudulent or safe.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| FastAPI | Backend and webhook |
| LangGraph | Multi-agent orchestration |
| Scikit-learn | Phishing classification |
| TF-IDF | Text feature extraction |
| Logistic Regression | Machine learning model |
| Joblib | Model persistence |
| SQLite | Telegram update tracking |
| Telegram Bot API | User interaction |
| Groq SDK | LLM and vision integration |
| Google Colab | Development and testing |
| GitHub | Version control |
| Render | Cloud hosting |

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rald10/NexMind-CyberSafe-AI.git
cd NexMind-CyberSafe-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows:

```bash
.venv\Scripts\activate
```

Activate on Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Configure the Telegram credentials and application settings required by the deployment.

For Groq integration:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit actual API keys or Telegram bot tokens to GitHub.

### 5. Start the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health endpoint:

```text
GET /health
```

Telegram webhook endpoint:

```text
POST /telegram/webhook
```

---

## 🚀 Deployment

CyberSafe AI is deployed on Render.

**Production Backend:**

https://nexmind-cybersafe-ai.onrender.com

**Health Endpoint:**

https://nexmind-cybersafe-ai.onrender.com/health

**Telegram Bot:**

https://t.me/NexmindCybersafe_bot

### Latest Recorded Deployment

| Detail | Value |
|---|---|
| Pull Request | #2 |
| Upgrade | Groq LLM and Vision Integration |
| Merge commit | `973bf3d` |
| Deployment method | Render Auto-Deploy |
| Deployment result | Live |

---

## 🧪 Testing and Validation

| Component | Recorded result |
|---|---|
| FastAPI health endpoint | Passed |
| Telegram webhook connection | Passed |
| Three-agent workflow | Passed |
| Phishing classifier inference | Passed |
| Telegram text analysis | Operational |
| Telegram automatic responses | Operational |
| Duplicate-update protection | Tested |
| Groq text analysis in Colab | Passed |
| Groq screenshot analysis in Colab | Passed |
| Offline upgrade smoke tests | Passed |
| GitHub PR #2 merge | Successful |
| Render upgrade deployment | Live |
| Groq contextual analysis on live Telegram | Not confirmed |
| Telegram screenshot analysis in production | Not confirmed |

---

## 🔐 Security and Privacy

The implementation includes:

- Telegram webhook secret validation.
- Duplicate-update protection.
- Environment-variable-based configuration.
- Preliminary risk explanations.
- Disclosure of incomplete external verification.

CyberSafe AI does not guarantee detection of every cybersecurity threat.

Users should avoid submitting real passwords, OTPs, PINs, or other sensitive credentials.

---

## 👥 Development Team

**Team Name:** NexMind

**Project Name:** CyberSafe AI

**Team Size:** 5 Members

**Project Category:** AI-Powered Cybersecurity Assistant

**Development Approach:** Multi-agent AI, machine learning, and Telegram integration.

---

## 📌 Current Project Status

### Operational

- Telegram text analysis.
- Machine learning phishing classification.
- Three-agent cybersecurity workflow.
- Heuristic risk scoring.
- Automated cybersecurity reports.
- Render-hosted FastAPI backend.

### Developed and Deployed but Not Yet Verified Live

- Groq contextual text explanations.
- Telegram screenshot analysis using Groq Vision.

---

## ⚠️ Disclaimer

CyberSafe AI provides preliminary cybersecurity assessments for awareness and educational purposes.

Its predictions, scores, and explanations should not be treated as definitive proof that content is malicious or safe.

External verification is identified as incomplete when the system has not independently verified a claim or link.

---

## 🔗 Project Links

- **GitHub:** https://github.com/Rald10/NexMind-CyberSafe-AI
- **Telegram:** https://t.me/NexmindCybersafe_bot
- **Backend:** https://nexmind-cybersafe-ai.onrender.com

---

**Developed by Team NexMind 🛡️**

*CyberSafe AI — Helping users recognize digital threats through intelligent cybersecurity analysis.*
