# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

from environment import TicketTriageEnvironment
from tasks import TASKS

app = FastAPI(title="Ticket Triage OpenEnv", version="1.0.0")
env = TicketTriageEnvironment()


# --------------------------------------------------
# Pydantic Models
# --------------------------------------------------

class ResetRequest(BaseModel):
    task_id: Optional[str] = Field(None)

class StepRequest(BaseModel):
    action: Dict[str, Any] = Field(...)


# --------------------------------------------------
# HTML Page (all buttons fixed)
# --------------------------------------------------

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Ticket Triage OpenEnv</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
header{background:linear-gradient(135deg,#1e40af,#7c3aed);padding:30px 40px;text-align:center}
header h1{font-size:2rem;font-weight:800;color:#fff}
header p{margin-top:8px;color:#bfdbfe;font-size:1rem}
.badge{display:inline-block;background:#22c55e;color:#fff;padding:4px 14px;border-radius:999px;font-size:.8rem;font-weight:700;margin-top:12px}
.container{max-width:960px;margin:36px auto;padding:0 20px}
.stats{display:flex;gap:14px;margin-bottom:28px;flex-wrap:wrap}
.sc{flex:1;min-width:130px;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:18px;text-align:center}
.sc .num{font-size:1.9rem;font-weight:800;color:#60a5fa}
.sc .lbl{font-size:.75rem;color:#94a3b8;margin-top:4px}
.card{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:26px;margin-bottom:24px}
.card h2{font-size:1.1rem;font-weight:700;color:#93c5fd;margin-bottom:16px}
.tgrid{display:flex;flex-direction:column;gap:10px}
.tc{background:#0f172a;border:1px solid #334155;border-radius:10px;padding:14px 18px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.tc h3{font-size:.95rem;font-weight:600}
.tc p{font-size:.78rem;color:#94a3b8;margin-top:2px}
.diff{padding:3px 11px;border-radius:999px;font-size:.72rem;font-weight:700}
.easy{background:#14532d;color:#4ade80}
.med{background:#713f12;color:#fbbf24}
.hard{background:#7f1d1d;color:#f87171}
.lbl{font-size:.8rem;color:#94a3b8;margin-bottom:6px}
select,textarea{width:100%;padding:11px 14px;border-radius:9px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:.9rem;outline:none;margin-bottom:10px}
textarea{height:100px;resize:vertical;font-family:monospace}
.btn{width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;font-size:.95rem;font-weight:700;cursor:pointer;transition:opacity .2s;margin-bottom:6px}
.btn:hover{opacity:.85}
.btn:active{opacity:.7}
.rbox{background:#020617;border:1px solid #1e3a5f;border-radius:9px;padding:14px;font-family:monospace;font-size:.82rem;color:#7dd3fc;white-space:pre-wrap;max-height:260px;overflow-y:auto;margin-top:8px;min-height:48px}
.rlbl{font-size:.78rem;color:#64748b;margin-top:10px;margin-bottom:4px}
.rbar-wrap{background:#0f172a;border-radius:999px;height:13px;margin:8px 0;overflow:hidden}
.rbar{height:100%;border-radius:999px;background:linear-gradient(90deg,#22c55e,#3b82f6);width:0%;transition:width .5s ease}
.rtxt{font-size:1.1rem;font-weight:800;color:#4ade80;text-align:center;margin-top:4px}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:.76rem;color:#64748b;padding:7px 10px;border-bottom:1px solid #1e293b}
td{padding:9px 10px;font-size:.83rem;border-bottom:1px solid #1e293b}
.m{display:inline-block;padding:2px 7px;border-radius:4px;font-size:.7rem;font-weight:700}
.get{background:#14532d;color:#4ade80}
.post{background:#1e3a5f;color:#60a5fa}
footer{text-align:center;color:#475569;font-size:.78rem;padding:28px 0 48px}
a{color:#60a5fa;text-decoration:none}
a:hover{text-decoration:underline}
.errtxt{color:#f87171;font-size:.82rem;margin-top:6px;display:none}
</style>
</head>
<body>
<header>
  <h1>&#127903; Ticket Triage OpenEnv</h1>
  <p>A real-world AI agent environment &#8212; built on the OpenEnv standard</p>
  <span class="badge">&#9989; RUNNING</span>
</header>

<div class="container">

  <div class="stats">
    <div class="sc"><div class="num">3</div><div class="lbl">Tasks</div></div>
    <div class="sc"><div class="num">6</div><div class="lbl">Sample Tickets</div></div>
    <div class="sc"><div class="num">7</div><div class="lbl">API Endpoints</div></div>
    <div class="sc"><div class="num" id="live-reward">&#8212;</div><div class="lbl">Last Reward</div></div>
  </div>

  <div class="card">
    <h2>&#128193; Available Tasks</h2>
    <div class="tgrid">
      <div class="tc">
        <div><h3>Task 1 &#8212; Ticket Categorization</h3><p>Classify the ticket into: billing | technical | general</p></div>
        <span class="diff easy">&#127894; EASY</span>
      </div>
      <div class="tc">
        <div><h3>Task 2 &#8212; Category + Priority</h3><p>Classify AND assign priority: low | medium | high</p></div>
        <span class="diff med">&#127893; MEDIUM</span>
      </div>
      <div class="tc">
        <div><h3>Task 3 &#8212; Full Ticket Triage</h3><p>Classify + prioritize + write a customer reply (min 10 words)</p></div>
        <span class="diff hard">&#128308; HARD</span>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>&#129514; Try It Live</h2>

    <div class="lbl">Step 1 &#8212; Pick a task then click Reset to get a ticket</div>
    <select id="task-select">
      <option value="task1_categorize">Task 1 &#8212; Categorize (Easy)</option>
      <option value="task2_prioritize">Task 2 &#8212; Category + Priority (Medium)</option>
      <option value="task3_full_triage">Task 3 &#8212; Full Triage (Hard)</option>
    </select>
    <button class="btn" id="reset-btn" onclick="doReset()">&#128260; Call /reset &#8212; Get a Ticket</button>
    <div class="rlbl">Response from /reset:</div>
    <div class="rbox" id="reset-box">Click the button above to get a ticket...</div>

    <br/>
    <div class="lbl">Step 2 &#8212; Edit your answer below then click Step</div>
    <textarea id="action-input">{ "category": "billing" }</textarea>
    <button class="btn" id="step-btn" onclick="doStep()">&#9889; Call /step &#8212; Submit Action and Get Reward</button>
    <div class="rlbl">Response from /step:</div>
    <div class="rbox" id="step-box">Click reset first, then submit your action here...</div>

    <div id="reward-wrap" style="display:none;margin-top:12px">
      <div class="lbl">Reward Score</div>
      <div class="rbar-wrap"><div class="rbar" id="rbar"></div></div>
      <div class="rtxt" id="rtxt"></div>
    </div>
  </div>

  <div class="card">
    <h2>&#128299; API Endpoints</h2>
    <table>
      <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
      <tr><td><span class="m get">GET</span></td><td>/</td><td>This UI dashboard</td></tr>
      <tr><td><span class="m post">POST</span></td><td>/reset</td><td>Start a new episode</td></tr>
      <tr><td><span class="m post">POST</span></td><td>/step</td><td>Submit action, get reward</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/state</td><td>Current environment state</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/tasks</td><td>List all tasks and schemas</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/grader</td><td>Last episode score</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/baseline</td><td>Run baseline agent</td></tr>
    </table>
    <br/>
    <a href="/docs" target="_blank">&#128214; Open Full API Docs (Swagger UI) &#8594;</a>
  </div>

</div>

<footer>
  Built for OpenEnv Round 1 &nbsp;|&nbsp;
  <a href="/docs" target="_blank">API Docs</a> &nbsp;|&nbsp;
  <a href="/tasks" target="_blank">Tasks JSON</a>
</footer>

<script>
var resetDone = false;

function setBox(id, text) {
  document.getElementById(id).textContent = text;
}

function updateAction(taskId) {
  var schemas = {
    "task1_categorize": '{ "category": "billing" }',
    "task2_prioritize": '{ "category": "billing", "priority": "high" }',
    "task3_full_triage": '{ "category": "billing", "priority": "high", "reply": "Thank you for contacting us. We will resolve your issue as soon as possible." }'
  };
  var el = document.getElementById("action-input");
  if (schemas[taskId]) { el.value = schemas[taskId]; }
}

function doReset() {
  var taskId = document.getElementById("task-select").value;
  setBox("reset-box", "Loading... please wait");
  updateAction(taskId);

  fetch("/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ "task_id": taskId })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    setBox("reset-box", JSON.stringify(data, null, 2));
    resetDone = true;
  })
  .catch(function(err) {
    setBox("reset-box", "ERROR: " + err.toString() + " — Try refreshing the page");
  });
}

function doStep() {
  var raw = document.getElementById("action-input").value;
  var action;
  try {
    action = JSON.parse(raw);
  } catch(e) {
    setBox("step-box", "JSON ERROR: Your action is not valid JSON.\nPlease check the format.\n\nExample: { \"category\": \"billing\" }");
    return;
  }

  setBox("step-box", "Loading... please wait");

  fetch("/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ "action": action })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    setBox("step-box", JSON.stringify(data, null, 2));
    if (data.reward !== undefined) {
      var r = parseFloat(data.reward);
      document.getElementById("reward-wrap").style.display = "block";
      document.getElementById("rbar").style.width = (r * 100) + "%";
      var msg = r >= 0.8 ? "Excellent! Score: " + r + " / 1.0" :
                r >= 0.5 ? "Partial Credit! Score: " + r + " / 1.0" :
                           "Wrong answer. Score: " + r + " / 1.0 — Try again";
      document.getElementById("rtxt").textContent = msg;
      document.getElementById("live-reward").textContent = r;
    }
    if (data.error) {
      setBox("step-box", "Server says: " + data.error + "\n\nPlease click Reset first!");
    }
  })
  .catch(function(err) {
    setBox("step-box", "ERROR: " + err.toString() + " — Try refreshing the page");
  });
}
</script>

</body>
</html>"""


# --------------------------------------------------
# API routes
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
    import inference as inf
    scores = inf.run_inference()
    return {"baseline_scores": scores}
