# main.py
# FastAPI server with typed Pydantic models (OpenEnv spec compliant)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

from environment import TicketTriageEnvironment
from tasks import TASKS

app = FastAPI(title="Ticket Triage OpenEnv", version="1.0.0")
env = TicketTriageEnvironment()


# --------------------------------------------------
# Typed Pydantic Models (OpenEnv spec requirement)
# --------------------------------------------------

class Observation(BaseModel):
    ticket_id: str = Field(..., description="Unique ticket identifier")
    subject:   str = Field(..., description="Subject line of the support ticket")
    body:      str = Field(..., description="Full body text of the support ticket")

class Action(BaseModel):
    category: str = Field(..., description="One of: billing | technical | general")
    priority: Optional[str] = Field(None, description="One of: low | medium | high")
    reply:    Optional[str] = Field(None, description="A helpful reply to the customer (min 10 words)")

class Reward(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0, description="Score between 0.0 and 1.0")
    done:  bool  = Field(..., description="Whether the episode is complete")
    info:  Dict[str, Any] = Field(default={}, description="Extra info (correct answers etc)")

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward:      float
    done:        bool
    info:        Dict[str, Any]

class ResetRequest(BaseModel):
    task_id: Optional[str] = Field(None, description="Task ID to run: task1_categorize | task2_prioritize | task3_full_triage")

class StepRequest(BaseModel):
    action: Dict[str, Any] = Field(..., description="Action dict matching the current task's action schema")


# --------------------------------------------------
# HTML Dashboard
# --------------------------------------------------

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Ticket Triage OpenEnv</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
    header { background: linear-gradient(135deg, #1e40af, #7c3aed); padding: 30px 40px; text-align: center; }
    header h1 { font-size: 2.2rem; font-weight: 800; color: #fff; }
    header p  { margin-top: 8px; color: #bfdbfe; font-size: 1rem; }
    .badge { display: inline-block; background: #22c55e; color: #fff; padding: 4px 14px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; margin-top: 12px; letter-spacing: 1px; }
    .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
    .stats { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
    .stat-card { flex: 1; min-width: 150px; background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; text-align: center; }
    .stat-card .num { font-size: 2rem; font-weight: 800; color: #60a5fa; }
    .stat-card .lbl { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
    .section { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 28px; margin-bottom: 28px; }
    .section h2 { font-size: 1.2rem; font-weight: 700; color: #93c5fd; margin-bottom: 18px; }
    .tasks-grid { display: flex; flex-direction: column; gap: 12px; }
    .task-card { background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
    .task-card .task-info h3 { font-size: 1rem; font-weight: 600; }
    .task-card .task-info p  { font-size: 0.8rem; color: #94a3b8; margin-top: 3px; }
    .difficulty { padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
    .easy   { background: #14532d; color: #4ade80; }
    .medium { background: #713f12; color: #fbbf24; }
    .hard   { background: #7f1d1d; color: #f87171; }
    .try-grid { display: flex; flex-direction: column; gap: 14px; }
    select, textarea, button { width: 100%; padding: 12px 16px; border-radius: 10px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.95rem; outline: none; }
    select:focus, textarea:focus { border-color: #3b82f6; }
    textarea { height: 110px; resize: vertical; font-family: monospace; }
    button { background: linear-gradient(135deg, #2563eb, #7c3aed); color: #fff; font-weight: 700; cursor: pointer; border: none; transition: opacity 0.2s; }
    button:hover { opacity: 0.88; }
    .label { font-size: 0.82rem; color: #94a3b8; margin-bottom: 5px; }
    .response-box { background: #020617; border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px; font-family: monospace; font-size: 0.85rem; color: #7dd3fc; white-space: pre-wrap; min-height: 60px; max-height: 280px; overflow-y: auto; display: none; }
    .response-box.visible { display: block; }
    .response-label { font-size: 0.8rem; color: #64748b; margin-bottom: 6px; margin-top: 12px; }
    .reward-bar-wrap { background: #0f172a; border-radius: 999px; height: 14px; margin: 10px 0; overflow: hidden; }
    .reward-bar { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #22c55e, #3b82f6); width: 0%; transition: width 0.6s ease; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; font-size: 0.78rem; color: #64748b; padding: 8px 12px; border-bottom: 1px solid #1e293b; }
    td { padding: 10px 12px; font-size: 0.85rem; border-bottom: 1px solid #1e293b; }
    .method { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; }
    .get  { background: #14532d; color: #4ade80; }
    .post { background: #1e3a5f; color: #60a5fa; }
    footer { text-align: center; color: #475569; font-size: 0.8rem; padding: 30px 0 50px; }
    a { color: #60a5fa; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<header>
  <h1>🎫 Ticket Triage OpenEnv</h1>
  <p>A real-world AI agent environment — built on the OpenEnv standard</p>
  <span class="badge">✅ RUNNING</span>
</header>
<div class="container">
  <div class="stats">
    <div class="stat-card"><div class="num">3</div><div class="lbl">Tasks</div></div>
    <div class="stat-card"><div class="num">6</div><div class="lbl">Sample Tickets</div></div>
    <div class="stat-card"><div class="num">7</div><div class="lbl">API Endpoints</div></div>
    <div class="stat-card"><div class="num" id="live-reward">—</div><div class="lbl">Last Reward</div></div>
  </div>
  <div class="section">
    <h2>🗂️ Available Tasks</h2>
    <div class="tasks-grid">
      <div class="task-card">
        <div class="task-info"><h3>Task 1 — Ticket Categorization</h3><p>Classify the ticket into: billing | technical | general</p></div>
        <span class="difficulty easy">🟢 EASY</span>
      </div>
      <div class="task-card">
        <div class="task-info"><h3>Task 2 — Category + Priority</h3><p>Classify AND assign priority: low | medium | high</p></div>
        <span class="difficulty medium">🟡 MEDIUM</span>
      </div>
      <div class="task-card">
        <div class="task-info"><h3>Task 3 — Full Ticket Triage</h3><p>Classify + prioritize + write a customer reply (min 10 words)</p></div>
        <span class="difficulty hard">🔴 HARD</span>
      </div>
    </div>
  </div>
  <div class="section">
    <h2>🧪 Try It Live</h2>
    <div class="try-grid">
      <div>
        <div class="label">Step 1 — Pick a task and get a ticket</div>
        <select id="task-select">
          <option value="task1_categorize">Task 1 — Categorize (Easy)</option>
          <option value="task2_prioritize">Task 2 — Category + Priority (Medium)</option>
          <option value="task3_full_triage">Task 3 — Full Triage (Hard)</option>
        </select>
        <br/><br/>
        <button onclick="doReset()">🔄 Call /reset — Get a Ticket</button>
        <div class="response-label">Response from /reset:</div>
        <div class="response-box" id="reset-box"></div>
      </div>
      <div>
        <div class="label">Step 2 — Submit your action (edit JSON below, then click step)</div>
        <textarea id="action-input">{\n  "category": "billing"\n}</textarea>
        <button onclick="doStep()">⚡ Call /step — Submit Action &amp; Get Reward</button>
        <div class="response-label">Response from /step:</div>
        <div class="response-box" id="step-box"></div>
        <div id="reward-section" style="display:none; margin-top:12px;">
          <div class="label">Reward Score</div>
          <div class="reward-bar-wrap"><div class="reward-bar" id="reward-bar"></div></div>
          <div id="reward-text" style="font-size:1.2rem;font-weight:800;color:#4ade80;text-align:center;margin-top:6px;"></div>
        </div>
      </div>
    </div>
  </div>
  <div class="section">
    <h2>🔌 API Endpoints</h2>
    <table>
      <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
      <tr><td><span class="method get">GET</span></td><td>/</td><td>This UI dashboard</td></tr>
      <tr><td><span class="method post">POST</span></td><td>/reset</td><td>Start a new episode</td></tr>
      <tr><td><span class="method post">POST</span></td><td>/step</td><td>Submit action, get reward</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/state</td><td>Current environment state</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/tasks</td><td>List all tasks + schemas</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/grader</td><td>Last episode score</td></tr>
      <tr><td><span class="method get">GET</span></td><td>/baseline</td><td>Run baseline agent</td></tr>
    </table>
    <br/>
    <a href="/docs" target="_blank">📖 Open Full API Docs (Swagger UI) →</a>
  </div>
</div>
<footer>Built for OpenEnv Round 1 &nbsp;|&nbsp; <a href="/docs" target="_blank">API Docs</a> &nbsp;|&nbsp; <a href="/tasks" target="_blank">Tasks JSON</a></footer>
<script>
  async function doReset() {
    const taskId = document.getElementById('task-select').value;
    const box = document.getElementById('reset-box');
    box.classList.add('visible'); box.textContent = 'Loading...';
    try {
      const res = await fetch('/reset', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({task_id: taskId}) });
      const data = await res.json();
      box.textContent = JSON.stringify(data, null, 2);
      const schemas = {
        task1_categorize: '{\n  "category": "billing"\n}',
        task2_prioritize: '{\n  "category": "billing",\n  "priority": "high"\n}',
        task3_full_triage: '{\n  "category": "billing",\n  "priority": "high",\n  "reply": "Thank you for reaching out. We will resolve your issue shortly."\n}'
      };
      document.getElementById('action-input').value = schemas[taskId] || '{}';
    } catch(e) { box.textContent = 'Error: ' + e.message; }
  }
  async function doStep() {
    const box = document.getElementById('step-box');
    box.classList.add('visible'); box.textContent = 'Loading...';
    let action = {};
    try { action = JSON.parse(document.getElementById('action-input').value); }
    catch(e) { box.textContent = 'Invalid JSON! Check your formatting.'; return; }
    try {
      const res = await fetch('/step', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({action}) });
      const data = await res.json();
      box.textContent = JSON.stringify(data, null, 2);
      if (data.reward !== undefined) {
        const r = data.reward;
        document.getElementById('reward-section').style.display = 'block';
        document.getElementById('reward-bar').style.width = (r * 100) + '%';
        const emoji = r >= 0.8 ? '🎉 Excellent!' : r >= 0.5 ? '👍 Partial Credit' : '❌ Try Again';
        document.getElementById('reward-text').textContent = 'Score: ' + r + ' / 1.0  ' + emoji;
        document.getElementById('live-reward').textContent = r;
      }
    } catch(e) { box.textContent = 'Error: ' + e.message; }
  }
</script>
</body>
</html>
"""


# --------------------------------------------------
# API Endpoints
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_PAGE


@app.post("/reset")
def reset(request: ResetRequest = None):
    task_id = request.task_id if request else None
    return env.reset(task_id=task_id)


@app.post("/step")
def step(request: StepRequest):
    return env.step(request.action)


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def list_tasks():
    return [
        {
            "task_id": t["task_id"],
            "name": t["name"],
            "description": t["description"],
            "difficulty": t["difficulty"],
            "action_schema": t["action_schema"],
        }
        for t in TASKS
    ]


@app.get("/grader")
def grader():
    s = env.state()
    return {
        "task_id": s["task_id"],
        "last_reward": s["last_reward"],
        "done": s["done"],
    }


@app.get("/baseline")
def baseline():
    import baseline as bl
    scores = bl.run_baseline()
    return {"baseline_scores": scores}