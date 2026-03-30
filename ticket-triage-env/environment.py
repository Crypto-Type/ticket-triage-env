# environment.py
# The core environment — handles reset(), step(), state()

import random
from tasks import TASKS, TICKETS


class TicketTriageEnvironment:

    def __init__(self):
        """Set up a blank environment."""
        self.current_task = None
        self.current_ticket = None
        self.step_count = 0
        self.last_reward = 0.0
        self.done = False

    # --------------------------------------------------
    # reset() — start a fresh episode
    # --------------------------------------------------
    def reset(self, task_id: str = None):
        """
        Start a new episode.
        - Picks the task (default: task1)
        - Picks a random ticket for the agent to solve
        """
        # Find the requested task, or default to first task
        if task_id:
            task = next((t for t in TASKS if t["task_id"] == task_id), TASKS[0])
        else:
            task = TASKS[0]

        self.current_task = task
        self.current_ticket = random.choice(TICKETS)
        self.step_count = 0
        self.last_reward = 0.0
        self.done = False

        return {
            "observation": {
                "ticket_id": self.current_ticket["id"],
                "subject": self.current_ticket["subject"],
                "body": self.current_ticket["body"],
            },
            "task_id": self.current_task["task_id"],
            "task_description": self.current_task["description"],
            "action_schema": self.current_task["action_schema"],
        }

    # --------------------------------------------------
    # step() — agent takes an action, get reward back
    # --------------------------------------------------
    def step(self, action: dict):
        """
        The agent submits an action (e.g. predicted category).
        We grade it and return a reward score between 0.0 and 1.0.
        """
        if self.done:
            return {"error": "Episode is finished. Please call reset() to start a new one."}

        if not self.current_task or not self.current_ticket:
            return {"error": "Environment not started. Please call reset() first."}

        # Score the action using the task's grader function
        grader_fn = self.current_task["grader"]
        reward = grader_fn(action, self.current_ticket)

        self.step_count += 1
        self.last_reward = reward
        self.done = True  # Each ticket = 1 step episode

        return {
            "observation": {
                "ticket_id": self.current_ticket["id"],
                "subject": self.current_ticket["subject"],
                "body": self.current_ticket["body"],
            },
            "reward": reward,
            "done": self.done,
            "info": {
                "step": self.step_count,
                "correct_category": self.current_ticket["correct_category"],
                "correct_priority": self.current_ticket["correct_priority"],
            },
        }

    # --------------------------------------------------
    # state() — what is the environment doing right now?
    # --------------------------------------------------
    def state(self):
        """Return the current state of the environment."""
        return {
            "task_id": self.current_task["task_id"] if self.current_task else None,
            "ticket_id": self.current_ticket["id"] if self.current_ticket else None,
            "step_count": self.step_count,
            "last_reward": self.last_reward,
            "done": self.done,
            "observation": {
                "subject": self.current_ticket["subject"] if self.current_ticket else None,
                "body": self.current_ticket["body"] if self.current_ticket else None,
            },
        }