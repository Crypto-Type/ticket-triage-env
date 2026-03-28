# 🎫 Ticket Triage OpenEnv

A real-world AI agent environment built on the OpenEnv standard.
An agent learns to triage customer support tickets — classifying, prioritizing, and replying.

---

## 🌍 Environment Description

Customer support teams receive hundreds of tickets daily. This environment trains an AI agent to:
1. **Classify** tickets (billing / technical / general)
2. **Prioritize** them (low / medium / high)
3. **Draft** a short helpful reply

---

## 🗂️ Tasks

| Task ID | Name | Difficulty | Score |
|---|---|---|---|
| `task1_categorize` | Ticket Categorization | 🟢 Easy | 0.0 or 1.0 |
| `task2_prioritize` | Category + Priority | 🟡 Medium | 0.0, 0.5, or 1.0 |
| `task3_full_triage` | Full Triage | 🔴 Hard | 0.0 – 1.0 |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/reset` | Start a new episode |
| POST | `/step` | Submit an action |
| GET | `/state` | Get current state |
| GET | `/tasks` | List all tasks + action schemas |
| GET | `/grader` | Get last episode score |
| GET | `/baseline` | Run baseline agent |

---

## 📥 Observation Space
```json
{
  "ticket_id": "T001",
  "subject": "I was charged twice",
  "body": "Full ticket text here..."
}
```

## 📤 Action Space

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
  "reply": "We apologize for the inconvenience and will process a refund shortly."
}
```

---

## 🚀 Local Setup
```bash
pip install fastapi uvicorn pydantic pyyaml
uvicorn main:app --host 0.0.0.0 --port 7860
python inference.py
```

---

## 🐳 Docker
```bash
docker build -t ticket-triage-env .
docker run -p 7860:7860 ticket-triage-env
```

---

## 📊 Reward Function

- **Task 1:** 1.0 if category correct, 0.0 otherwise
- **Task 2:** 0.5 per correct field (category + priority)
- **Task 3:** ~0.34 per correct field (category + priority + reply ≥10 words)
