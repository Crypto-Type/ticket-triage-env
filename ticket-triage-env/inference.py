# inference.py
# Competition-required inference script
# Uses OpenAI client to run an LLM agent against all 3 tasks
# Reads credentials from environment variables:
#   API_BASE_URL  — the LLM API endpoint
#   MODEL_NAME    — the model identifier
#   HF_TOKEN      — your Hugging Face / API key

import os
import json
import requests
from openai import OpenAI

# --------------------------------------------------
# Read credentials from environment variables
# --------------------------------------------------
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.environ.get("HF_TOKEN",     "")

# The URL of your running OpenEnv environment
ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

# --------------------------------------------------
# Set up the OpenAI-compatible client
# --------------------------------------------------
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

# --------------------------------------------------
# Helper: call the environment API
# --------------------------------------------------

def env_reset(task_id: str) -> dict:
    """Call /reset on the environment."""
    res = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30
    )
    res.raise_for_status()
    return res.json()


def env_step(action: dict) -> dict:
    """Call /step on the environment."""
    res = requests.post(
        f"{ENV_BASE_URL}/step",
        json={"action": action},
        timeout=30
    )
    res.raise_for_status()
    return res.json()


# --------------------------------------------------
# The LLM Agent — builds a prompt and calls the model
# --------------------------------------------------

def llm_agent(observation: dict, task_id: str, action_schema: dict) -> dict:
    """
    Given a ticket observation, ask the LLM to produce the correct action.
    Returns a dict matching the action schema for the task.
    """

    # Build a clear prompt for the LLM
    system_prompt = """You are a customer support triage expert.
You will be given a support ticket and you must analyze it carefully.
You must respond ONLY with a valid JSON object matching the requested schema.
Do not include any explanation, just the JSON object."""

    schema_str = json.dumps(action_schema, indent=2)

    user_prompt = f"""Here is a customer support ticket:

Subject: {observation.get('subject', '')}
Body: {observation.get('body', '')}

Your task: {task_id}

Respond ONLY with a JSON object using this exact schema:
{schema_str}

Rules:
- category must be exactly one of: billing, technical, general
- priority must be exactly one of: low, medium, high  
- reply (if required) must be at least 10 words long and helpful

Respond with ONLY the JSON object, nothing else."""

    # Call the LLM
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        # Clean up: remove markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        action = json.loads(raw)
        return action

    except Exception as e:
        print(f"  [LLM Error] {e} — using fallback random action")
        # Fallback if LLM fails
        import random
        fallback = {"category": random.choice(["billing", "technical", "general"])}
        if "priority" in action_schema:
            fallback["priority"] = random.choice(["low", "medium", "high"])
        if "reply" in action_schema:
            fallback["reply"] = "Thank you for contacting us. We will look into your issue and respond shortly."
        return fallback


# --------------------------------------------------
# Run inference on all 3 tasks
# --------------------------------------------------

TASKS = [
    {
        "task_id": "task1_categorize",
        "action_schema": {
            "category": "string — one of: billing | technical | general"
        }
    },
    {
        "task_id": "task2_prioritize",
        "action_schema": {
            "category": "string — one of: billing | technical | general",
            "priority": "string — one of: low | medium | high"
        }
    },
    {
        "task_id": "task3_full_triage",
        "action_schema": {
            "category": "string — one of: billing | technical | general",
            "priority": "string — one of: low | medium | high",
            "reply": "string — a short helpful reply to the customer (min 10 words)"
        }
    },
]

EPISODES_PER_TASK = 5   # Run 5 episodes per task (keep under 20 min limit)


def run_inference():
    """Run the LLM agent against all 3 tasks and report scores."""
    print("=" * 60)
    print("TICKET TRIAGE OPENENV — LLM INFERENCE SCRIPT")
    print(f"Model      : {MODEL_NAME}")
    print(f"API Base   : {API_BASE_URL}")
    print(f"Env URL    : {ENV_BASE_URL}")
    print("=" * 60)

    all_results = {}

    for task in TASKS:
        task_id = task["task_id"]
        action_schema = task["action_schema"]
        total_reward = 0.0

        print(f"\n▶ Running task: {task_id}")
        print(f"  Episodes: {EPISODES_PER_TASK}")

        for ep in range(EPISODES_PER_TASK):
            try:
                # Step 1: Reset the environment
                obs_data = env_reset(task_id)
                observation = obs_data.get("observation", {})

                # Step 2: Ask the LLM for an action
                action = llm_agent(observation, task_id, action_schema)
                print(f"  Episode {ep+1}: action={json.dumps(action)}")

                # Step 3: Submit action to environment
                result = env_step(action)
                reward = result.get("reward", 0.0)
                total_reward += reward
                print(f"            reward={reward}")

            except Exception as e:
                print(f"  Episode {ep+1}: ERROR — {e}")

        avg_reward = round(total_reward / EPISODES_PER_TASK, 3)
        all_results[task_id] = {
            "average_reward": avg_reward,
            "episodes_run": EPISODES_PER_TASK,
        }
        print(f"  ✅ Average Reward for {task_id}: {avg_reward}")

    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    for task_id, result in all_results.items():
        print(f"  {task_id:35s} → {result['average_reward']}")
    print("=" * 60)

    return all_results


# Run when called directly: python inference.py
if __name__ == "__main__":
    run_inference()
    