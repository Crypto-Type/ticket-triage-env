Title: Ticket Triage Env
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

Every company — from startups to Fortune 500s — receives **hundreds of customer support tickets every day**. Human agents must read each ticket, decide what type of problem it is, how urgent it is, and craft a helpful response. This process is:

- ⏱️ **Time-consuming** — reading and triaging takes hours daily
- 🤔 **Judgment-heavy** — requires experience and domain knowledge  
- 📈 **Scalability bottleneck** — hard to scale with growing user bases

**This environment trains AI agents to automate that entire workflow** — from reading a raw ticket to producing a complete, prioritized response. It's a direct, practical training ground for agents that could save real companies thousands of hours annually.

---

## 🏗️ Environment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  AI Agent  (My Model)                    │
│                        │                                 │
│              ┌─────────▼──────────┐                      │
│              │   OpenEnv API      │                      │
│              │  POST /reset       │  ← Get a ticket      │
│              │  POST /step        │  ← Submit answer     │
│              │  GET  /state       │  ← Check status      │
│              └─────────┬──────────┘                      │
│                        │                                 │
│              ┌─────────▼──────────┐                      │
│              │  TicketTriage Env  │                      │
│              │  environment.py    │                      │
│              └─────────┬──────────┘                      │
│                        │                                 │
│         ┌──────────────┼──────────────┐                  │
│         ▼              ▼              ▼                  │
│    Task 1 Grader  Task 2 Grader  Task 3 Grader           │
│    (Easy)         (Medium)       (Hard)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Tasks Overview

The environment presents **3 tasks of increasing difficulty**, each requiring deeper understanding of the support ticket.

### 🟢 Task 1 — Ticket Categorization `(Easy)`
> **Objective:** Read a support ticket and classify it into the correct category.

| Field | Details |
|---|---|
| **Task ID** | `task1_categorize` |
| **Input** | Ticket subject + body text |
| **Output** | Category label |
| **Valid Values** | `billing` · `technical` · `general` |
| **Scoring** | `1.0` if correct · `0.0` if wrong |
| **Why it matters** | Routing tickets to the right team is the first step in any triage pipeline |

**Example:**
```
Subject: "I was charged twice for my subscription"
Body:    "I noticed two charges of $29.99 this month..."

Correct action:  { "category": "billing" }
Reward:          1.0
```

---

### 🟡 Task 2 — Category + Priority Assignment `(Medium)`
> **Objective:** Classify the ticket AND determine how urgent it is.

| Field | Details |
|---|---|
| **Task ID** | `task2_prioritize` |
| **Input** | Ticket subject + body text |
| **Output** | Category + priority label |
| **Valid Categories** | `billing` · `technical` · `general` |
| **Valid Priorities** | `low` · `medium` · `high` |
| **Scoring** | `0.5` per correct field · max `1.0` |
| **Why it matters** | Priority determines SLA response times — wrong priority = unhappy customers |

**Example:**
```
Subject: "App keeps crashing on login"
Body:    "Every time I try to log in it crashes immediately..."

Correct action:  { "category": "technical", "priority": "high" }
Reward:          1.0  (both fields correct)
                 0.5  (only one field correct)
                 0.0  (both wrong)
```

---

### 🔴 Task 3 — Full Ticket Triage `(Hard)`
> **Objective:** Classify, prioritize, AND draft a helpful customer reply.

| Field | Details |
|---|---|
| **Task ID** | `task3_full_triage` |
| **Input** | Ticket subject + body text |
| **Output** | Category + priority + customer reply |
| **Reply Requirement** | Minimum 10 words, helpful and contextual |
| **Scoring** | ~`0.34` per correct field · max `1.0` |
| **Why it matters** | Combines understanding, judgment, and communication — the full triage workflow |

**Example:**
```
Subject: "Payment failed but money was deducted"
Body:    "I tried to upgrade but payment failed, money gone..."

Correct action: {
  "category": "billing",
  "priority": "high",
  "reply": "We sincerely apologize for this inconvenience. Our billing
            team will investigate and process your refund within 24 hours."
}
Reward: 1.0
```

---

## 📐 Observation & Action Spaces

### Observation Space
What the agent receives at the start of each episode:

```json
{
  "observation": {
    "ticket_id": "T001",
    "subject":   "I was charged twice for my subscription",
    "body":      "Hello, I noticed two charges of $29.99 on my credit card..."
  },
  "task_id":          "task1_categorize",
  "task_description": "Classify the support ticket into: billing, technical, or general",
  "action_schema": {
    "category": "string — one of: billing | technical | general"
  }
}
```

### Action Space (per task)

**Task 1:**
```json
{ "category": "billing" }
```

**Task 2:**
```json
{ "category": "billing", "priority": "high" }
```

**Task 3:**
```json
{
  "category": "billing",
  "priority": "high",
  "reply": "Thank you for contacting us. We will resolve your issue within 24 hours."
}
```

---

## 🏆 Reward Function Design

The reward function is designed to provide **dense, partial credit signals** — not just binary pass/fail. This is intentional: it helps AI agents learn faster by knowing which parts of their answer were correct.

```
Task 1 reward:
  R = 1.0 if category correct else 0.0

Task 2 reward:
  R = (0.5 × category_correct) + (0.5 × priority_correct)

Task 3 reward:
  R = (0.34 × category_correct)
    + (0.33 × priority_correct)
    + (0.33 × reply_length >= 10 words)
```

**Why this matters for learning:**
- A random agent scores ~0.33 on Task 1 (1 in 3 chance of guessing right)
- A smart agent scores ~0.85+ by reading the ticket carefully
- The gap between random and smart is **measurable and large** — ideal for training

---

## 🔌 API Reference

Base URL: `https://aadhesh2025-ticket-triage-env.hf.space`

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/` | Live dashboard UI | — |
| `POST` | `/reset` | Start new episode | `{"task_id": "task1_categorize"}` |
| `POST` | `/step` | Submit action, get reward | `{"action": {"category": "billing"}}` |
| `GET` | `/state` | Current environment state | — |
| `GET` | `/tasks` | List all tasks + schemas | — |
| `GET` | `/grader` | Last episode score | — |
| `GET` | `/baseline` | Run baseline agent | — |

### Quick Example (curl)

```bash
# Start an episode
curl -X POST https://aadhesh2025-ticket-triage-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task1_categorize"}'

# Submit your answer
curl -X POST https://aadhesh2025-ticket-triage-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"category": "billing"}}'
```

### Quick Example (Python)

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

Scores achieved by a **random agent** (picks answers randomly):

| Task | Avg Reward | Episodes |
|---|---|---|
| `task1_categorize` | ~0.33 | 20 |
| `task2_prioritize` | ~0.28 | 20 |
| `task3_full_triage` | ~0.56 | 20 |

> 💡 A well-trained LLM agent is expected to score **0.80+** on all tasks. The gap between random (~0.33) and optimal (~1.0) provides strong training signal.

---

## 🚀 Local Setup

### Prerequisites
- Python 3.9+
- pip

### Install and Run

```bash
# 1. Clone the repository
git clone https://github.com/Crypto-Type/ticket-triage-env
cd ticket-triage-env

# 2. Install dependencies
pip install -e .

# 3. Start the server
uvicorn main:app --host 0.0.0.0 --port 7860 --reload

# 4. Open in browser
# http://localhost:7860
```

### Run Baseline Agent

```bash
python baseline.py
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
# Build
docker build -t ticket-triage-env .

# Run
docker run -p 7860:7860 ticket-triage-env

# Open: http://localhost:7860
```

---

## 📁 Project Structure

```
ticket-triage-env/
│
├── main.py           # FastAPI server + visual dashboard UI
├── environment.py    # Core env logic: reset(), step(), state()
├── tasks.py          # Task definitions, ticket dataset, graders
├── inference.py      # LLM inference script (OpenAI client)
├── baseline.py       # Random baseline agent
├── openenv.yaml      # OpenEnv specification file
├── pyproject.toml    # Python project configuration
├── Dockerfile        # Container definition for HF Spaces
└── README.md         # This file
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

## 🤖 Writing Your Own Agent

```python
import requests

BASE = "https://aadhesh2025-ticket-triage-env.hf.space"

def my_agent(observation):
    """Your agent logic here."""
    subject = observation["subject"].lower()
    body    = observation["body"].lower()

    # Simple rule-based agent
    if any(word in body for word in ["charge", "payment", "refund", "billing"]):
        return {"category": "billing", "priority": "high"}
    elif any(word in body for word in ["crash", "error", "bug", "broken"]):
        return {"category": "technical", "priority": "high"}
    else:
        return {"category": "general", "priority": "low"}

# Run one episode
obs_data = requests.post(f"{BASE}/reset", json={"task_id": "task2_prioritize"}).json()
action   = my_agent(obs_data["observation"])
result   = requests.post(f"{BASE}/step", json={"action": action}).json()

print(f"Action: {action}")
print(f"Reward: {result['reward']}")
print(f"Correct: {result['info']}")
```

---

## 📋 OpenEnv Compliance

This environment implements the full OpenEnv specification:

- ✅ Typed Pydantic models for Observation, Action, Reward
- ✅ `POST /reset` — returns clean initial observation
- ✅ `POST /step` — returns observation, reward, done, info
- ✅ `GET /state` — returns current environment state
- ✅ `openenv.yaml` with full metadata
- ✅ Deployed on Hugging Face Spaces
- ✅ Working Dockerfile
- ✅ `inference.py` using OpenAI-compatible client
- ✅ Scores reproducible between runs

---

## 👤 Author

**Aravind S**  
Built for OpenEnv Round 1 — Hugging Face × Meta AI Competition

---

<div align="center">

**Built with ❤️ using FastAPI · Docker · Hugging Face Spaces**

[🚀 Try it Live](https://aadhesh2025-ticket-triage-env.hf.space) · [📖 API Docs](https://aadhesh2025-ticket-triage-env.hf.space/docs)

</div>
