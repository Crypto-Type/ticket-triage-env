# tasks.py
# Defines the 3 tasks and their graders (scoring functions)

VALID_CATEGORIES = ["billing", "technical", "general"]
VALID_PRIORITIES = ["low", "medium", "high"]

# ------------------------------------
# Sample support tickets (our dataset)
# ------------------------------------
TICKETS = [
    {
        "id": "T001",
        "subject": "I was charged twice for my subscription",
        "body": "Hello, I noticed two charges of $29.99 on my credit card this month. Please refund the duplicate charge.",
        "correct_category": "billing",
        "correct_priority": "high",
    },
    {
        "id": "T002",
        "subject": "App keeps crashing on login",
        "body": "Every time I try to log in to the app on my iPhone, it crashes immediately. I have tried reinstalling but it still happens.",
        "correct_category": "technical",
        "correct_priority": "high",
    },
    {
        "id": "T003",
        "subject": "How do I change my username?",
        "body": "I would like to update my username on my account. Could you please let me know the steps to do this?",
        "correct_category": "general",
        "correct_priority": "low",
    },
    {
        "id": "T004",
        "subject": "Payment failed but money was deducted",
        "body": "I tried to upgrade my plan but the payment failed. However, the money has been deducted from my account.",
        "correct_category": "billing",
        "correct_priority": "high",
    },
    {
        "id": "T005",
        "subject": "Cannot download my invoice",
        "body": "The download button for my monthly invoice is not working. I need the invoice for tax purposes.",
        "correct_category": "technical",
        "correct_priority": "medium",
    },
    {
        "id": "T006",
        "subject": "Where can I find your privacy policy?",
        "body": "I need to read your privacy policy for compliance reasons. Could you share the link?",
        "correct_category": "general",
        "correct_priority": "low",
    },
]


# ------------------------------------
# Graders — these score the agent
# ------------------------------------

def grade_task1(action: dict, ticket: dict) -> float:
    """
    Task 1 (Easy): Just classify the category.
    Score: 1.0 if correct, 0.0 if wrong.
    """
    predicted = action.get("category", "").lower().strip()
    correct = ticket["correct_category"]
    return 1.0 if predicted == correct else 0.0


def grade_task2(action: dict, ticket: dict) -> float:
    """
    Task 2 (Medium): Classify category + assign priority.
    Score: 0.5 per correct field. Max = 1.0
    """
    score = 0.0
    predicted_cat = action.get("category", "").lower().strip()
    predicted_pri = action.get("priority", "").lower().strip()

    if predicted_cat == ticket["correct_category"]:
        score += 0.5
    if predicted_pri == ticket["correct_priority"]:
        score += 0.5
    return score


def grade_task3(action: dict, ticket: dict) -> float:
    """
    Task 3 (Hard): Classify + prioritize + write a reply.
    Score: ~0.34 per correct field. Max = 1.0
    Reply must be at least 10 words to get points.
    """
    score = 0.0
    predicted_cat = action.get("category", "").lower().strip()
    predicted_pri = action.get("priority", "").lower().strip()
    reply = action.get("reply", "").strip()

    if predicted_cat == ticket["correct_category"]:
        score += 0.34
    if predicted_pri == ticket["correct_priority"]:
        score += 0.33
    if len(reply.split()) >= 10:
        score += 0.33
    return round(score, 2)


# ------------------------------------
# Task definitions (used by the API)
# ------------------------------------

TASKS = [
    {
        "task_id": "task1_categorize",
        "name": "Ticket Categorization",
        "description": "Classify the support ticket into: billing, technical, or general",
        "difficulty": "easy",
        "action_schema": {
            "category": "string — one of: billing | technical | general"
        },
        "grader": grade_task1,
    },
    {
        "task_id": "task2_prioritize",
        "name": "Ticket Categorization + Priority",
        "description": "Classify the ticket AND assign a priority: low, medium, or high",
        "difficulty": "medium",
        "action_schema": {
            "category": "string — one of: billing | technical | general",
            "priority": "string — one of: low | medium | high",
        },
        "grader": grade_task2,
    },
    {
        "task_id": "task3_full_triage",
        "name": "Full Ticket Triage",
        "description": "Classify, prioritize, AND write a short helpful reply to the customer",
        "difficulty": "hard",
        "action_schema": {
            "category": "string — one of: billing | technical | general",
            "priority": "string — one of: low | medium | high",
            "reply": "string — a short helpful reply to the customer (min 10 words)",
        },
        "grader": grade_task3,
    },
]