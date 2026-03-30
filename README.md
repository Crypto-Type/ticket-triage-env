---
title: Ticket Triage Env
emoji: 🎫
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
tags:
  - openenv
  - reinforcement-learning
  - ai-agent
  - customer-support
  - nlp
---

<div align="center">

# 🎫 Ticket Triage OpenEnv

### A Real-World AI Agent Training Environment

**Train AI agents to triage customer support tickets — classify, prioritize, and respond.**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-22c55e?style=for-the-badge)](https://huggingface.co/spaces/aadhesh2025/ticket-triage-env)
[![HF Space](https://img.shields.io/badge/HuggingFace-Space-ff9d00?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/aadhesh2025/ticket-triage-env)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed?style=for-the-badge&logo=docker)](https://github.com/Crypto-Type/ticket-triage-env)
[![Python](https://img.shields.io/badge/Python-3.11-3776ab?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

[🚀 Live Demo](https://aadhesh2025-ticket-triage-env.hf.space) · [📖 API Docs](https://aadhesh2025-ticket-triage-env.hf.space/docs) · [📋 Tasks](https://aadhesh2025-ticket-triage-env.hf.space/tasks)

</div>

---

## 🌍 Why This Environment Exists

Every company receives **hundreds of customer support tickets every day**. Human agents must read each ticket, decide what type of problem it is, how urgent it is, and craft a helpful response. This process is:

- ⏱️ **Time-consuming** — reading and triaging takes hours daily
- 🤔 **Judgment-heavy** — requires experience and domain knowledge
- 📈 **Scalability bottleneck** — hard to scale with growing user bases

**This environment trains AI agents to automate that entire workflow.**

---

## 🏗️ Environment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  AI Agent (your model)                  │
│                        │                                │
│              ┌─────────▼──────────┐                     │
│              │   OpenEnv API      │                     │
│              │  POST /reset       │  ← Get a ticket     │
│              │  POST /step        │  ← Submit answer    │
│              │  GET  /state       │  ← Check status     │
│              └─────────┬──────────┘                     │
│                        │                                │
│              ┌─────────▼──────────┐                     │
│              │  TicketTriage Env  │                     │
│              │  environment.py    │                     │
│              └─────────┬──────────┘                     │
│                        │                                │
│         ┌──────────────┼──────────────┐                 │
│         ▼              ▼              ▼                 │
│    Task 1 Grader  Task 2 Grader  Task 3 Grader          │
│    (Easy)         (Medium)       (Hard)                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Tasks Overview

### 🟢 Task 1 — Ticket Categorization `(Easy)`

| Field | Details |
|---|---|
| **Task ID** | `task1_categorize` |
| **Input** | Ticket subject + body text |
| **Output** | Category label |
| **Valid Values** | `billing` · `technical` · `general` |
| **Scoring** | `1.0` if correct · `0.0` if wrong |

**Example:**
```json
Input:  "I was charged twice for my subscription"
Action: { "category": "billing" }
Reward: 1.0
```

---

### 🟡 Task 2 — Category + Priority Assignment `(Medium)`

| Field | Details |
|---|---|
| **Task ID** | `task2_prioritize` |
| **Input** | Ticket subject + body text |
| **Output** | Category + priority label |
| **Valid Priorities** | `low` · `medium` · `high` |
| **Scoring** | `0.5` per correct field · max `1.0` |

**Example:**
```json
Action: { "category": "technical", "priority": "high" }
Reward: 1.0  (both correct) | 0.5  (one correct) | 0.0  (both wrong)
```

---

### 🔴 Task 3 — Full Ticket Triage `(Hard)`

| Field | Details |
|---|---|
| **Task ID** | `task3_full_triage` |
| **Input** | Ticket subject + body text |
| **Output** | Category + priority + customer reply |
| **Reply Requirement** | Minimum 10 words |
| **Scoring** | `~0.34` per correct field · max `1.0` |

**Example:**
```json
Action: {
  "category": "billing",
  "priority": "high",
  "reply": "We sincerely apologize. Our billing team will process your refund within 24 hours."
}
Reward: 1.0
```

---

## 📐 Observation & Action Spaces

### Observation Space
```json
{
  "observation": {
    "ticket_id": "T001",
    "subject":   "I was charged twice for my subscription",
    "body":      "Hello, I noticed two charges of $29.99 on my credit card..."
  },
  "task_id": "task1_categorize",
  "task_description": "Classify the support ticket into: billing, technical, or general",
  "action_schema": {
    "category": "string — one of: billing | technical | general"
  }
}
```

### Action Space

**Task 1:** `{ "category": "billing" }`

**Task 2:** `{ "category": "billing", "priority": "high" }`

**Task 3:**
```json
{
  "category": "billing",
  "priority": "high",
  "reply": "Thank you for contacting us. We will resolve your issue within 24 hours."
}
```

---

## 🏆 Reward Function

```
Task 1:  R = 1.0 if category correct, else 0.0

Task 2:  R = (0.5 × category_correct) + (0.5 × priority_correct)

Task 3:  R = (0.34 × category_correct)
           + (0.33 × priority_correct)
           + (0.33 × reply_length >= 10 words)
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Live dashboard UI |
| `POST` | `/reset` | Start new episode |
| `POST` | `/step` | Submit action, get reward |
| `GET` | `/state` | Current environment state |
| `GET` | `/tasks` | List all tasks + schemas |
| `GET` | `/grader` | Last episode score |
| `GET` | `/baseline` | Run baseline agent |

### Python Example

```python
import requests

BASE = "https://aadhesh2025-ticket-triage-env.hf.space"

# Start episode
obs = requests.post(f"{BASE}/reset", json={"task_id": "task1_categorize"}).json()
print(obs["observation"]["subject"])

# Submit action
result = requests.post(f"{BASE}/step", json={"action": {"category": "billing"}}).json()
print(f"Reward: {result['reward']}")
```

---

## 📊 Baseline Scores

| Task | Avg Reward | Agent Type |
|---|---|---|
| `task1_categorize` | ~0.33 | Random agent |
| `task2_prioritize` | ~0.28 | Random agent |
| `task3_full_triage` | ~0.56 | Random agent |

---

## 🚀 Local Setup

```bash
# Clone
git clone https://github.com/Crypto-Type/ticket-triage-env
cd ticket-triage-env

# Install
pip install -r requirements.txt

# Run
uvicorn main:app --host 0.0.0.0 --port 7860 --reload

# Open: http://localhost:7860
```

### Run Inference Script

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your_hf_token_here"
export ENV_BASE_URL="http://localhost:7860"

python inference.py
```

---

## 🐳 Docker

```bash
docker build -t ticket-triage-env .
docker run -p 7860:7860 ticket-triage-env
```

---

## 📁 Project Structure

```
ticket-triage-env/
├── main.py            # FastAPI server + UI dashboard
├── environment.py     # Core env: reset(), step(), state()
├── tasks.py           # Tasks, tickets, grader functions
├── inference.py       # LLM inference script (OpenAI client)
├── baseline.py        # Random baseline agent
├── openenv.yaml       # OpenEnv specification
├── pyproject.toml     # Python project config
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container definition
└── README.md          # This file
```

---

## 🧪 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `API_BASE_URL` | LLM API endpoint | `https://api-inference.huggingface.co/v1` |
| `MODEL_NAME` | Model identifier | `Qwen/Qwen2.5-72B-Instruct` |
| `HF_TOKEN` | Hugging Face API key | `""` |
| `ENV_BASE_URL` | Environment server URL | `http://localhost:7860` |

---

## 📋 OpenEnv Compliance

- ✅ Typed Pydantic models for Observation, Action, Reward
- ✅ `POST /reset` — returns clean initial observation
- ✅ `POST /step` — returns observation, reward, done, info
- ✅ `GET /state` — returns current environment state
- ✅ `openenv.yaml` with full metadata
- ✅ Deployed on Hugging Face Spaces with Docker
- ✅ `inference.py` using OpenAI-compatible client
- ✅ Scores reproducible between runs

---

## 👤 Author

**Aravind S** — Built for OpenEnv Round 1 · Hugging Face × Meta AI Competition

---

<div align="center">

**Built with ❤️ using FastAPI · Docker · Hugging Face Spaces**

[🚀 Try it Live](https://aadhesh2025-ticket-triage-env.hf.space) · [📖 API Docs](https://aadhesh2025-ticket-triage-env.hf.space/docs)

</div>
