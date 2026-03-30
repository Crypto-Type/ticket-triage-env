# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

from environment import TicketTriageEnvironment
from tasks import TASKS

app = FastAPI(title="Ticket Triage OpenEnv", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = TicketTriageEnvironment()


class ResetRequest(BaseModel):
    task_id: Optional[str] = Field(None)

class StepRequest(BaseModel):
    action: Dict[str, Any] = Field(...)


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Ticket Triage OpenEnv</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
header{background:linear-gradient(135deg,#1e40af,#7c3aed);padding:28px 20px;text-align:center}
header h1{font-size:1.8rem;font-weight:800;color:#fff}
header p{margin-top:6px;color:#bfdbfe;font-size:.92rem}
.badge{display:inline-block;background:#22c55e;color:#fff;padding:4px 14px;border-radius:999px;font-size:.76rem;font-weight:700;margin-top:10px}
.container{max-width:880px;margin:28px auto;padding:0 16px}
.stats{display:flex;gap:12px;margin-bottom:22px;flex-wrap:wrap}
.sc{flex:1;min-width:110px;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:15px;text-align:center}
.sc .num{font-size:1.7rem;font-weight:800;color:#60a5fa}
.sc .lbl{font-size:.7rem;color:#94a3b8;margin-top:3px}
.card{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:20px;margin-bottom:20px}
.card h2{font-size:1rem;font-weight:700;color:#93c5fd;margin-bottom:14px}
.tgrid{display:flex;flex-direction:column;gap:9px}
.tc{background:#0f172a;border:1px solid #334155;border-radius:10px;padding:12px 15px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.tc h3{font-size:.88rem;font-weight:600}
.tc p{font-size:.74rem;color:#94a3b8;margin-top:2px}
.diff{padding:3px 10px;border-radius:999px;font-size:.68rem;font-weight:700}
.easy{background:#14532d;color:#4ade80}
.med{background:#713f12;color:#fbbf24}
.hard{background:#7f1d1d;color:#f87171}
.lbl{font-size:.78rem;color:#94a3b8;margin-bottom:5px;margin-top:6px}
select{width:100%;padding:10px 12px;border-radius:9px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:.86rem;outline:none;margin-bottom:10px}
textarea{width:100%;padding:10px 12px;border-radius:9px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:.86rem;outline:none;height:86px;resize:vertical;font-family:monospace;margin-bottom:10px}
.btn{width:100%;padding:12px;border-radius:10px;border:2px solid #3b82f6;background:linear-gradient(135deg,#1d4ed8,#6d28d9);color:#fff;font-size:.92rem;font-weight:700;cursor:pointer;margin-bottom:8px;letter-spacing:.3px}
.btn:hover{background:linear-gradient(135deg,#2563eb,#7c3aed);border-color:#60a5fa}
.btn:active{transform:scale(.98);opacity:.8}
.rbox{background:#020617;border:2px solid #1e3a5f;border-radius:9px;padding:13px;font-family:monospace;font-size:.78rem;color:#7dd3fc;white-space:pre-wrap;max-height:220px;overflow-y:auto;min-height:50px;word-break:break-all;margin-top:6px}
.rbox.ok{border-color:#22c55e;color:#86efac}
.rbox.err{border-color:#ef4444;color:#fca5a5}
.rbox.loading{border-color:#f59e0b;color:#fcd34d}
.rlbl{font-size:.75rem;color:#64748b;margin-top:10px;margin-bottom:4px}
.rbar-wrap{background:#0f172a;border-radius:999px;height:14px;margin:8px 0;overflow:hidden;border:1px solid #334155}
.rbar{height:100%;border-radius:999px;background:linear-gradient(90deg,#22c55e,#3b82f6);width:0%;transition:width .6s}
.rtxt{font-size:1rem;font-weight:800;text-align:center;margin-top:6px;padding:8px;border-radius:8px}
.rtxt.good{color:#4ade80;background:#052e16}
.rtxt.mid{color:#fbbf24;background:#1c1200}
.rtxt.bad{color:#f87171;background:#1c0000}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:.72rem;color:#64748b;padding:7px 9px;border-bottom:1px solid #1e293b}
td{padding:8px 9px;font-size:.8rem;border-bottom:1px solid #1e293b}
.m{display:inline-block;padding:2px 7px;border-radius:4px;font-size:.67rem;font-weight:700}
.get{background:#14532d;color:#4ade80}
.post{background:#1e3a5f;color:#60a5fa}
footer{text-align:center;color:#475569;font-size:.74rem;padding:22px 0 38px}
a{color:#60a5fa;text-decoration:none}
a:hover{text-decoration:underline}
.debug{background:#1a0a00;border:1px solid #92400e;border-radius:8px;padding:10px;font-size:.72rem;color:#fcd34d;font-family:monospace;margin-top:8px;white-space:pre-wrap;max-height:80px;overflow-y:auto}
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
    <div class="sc"><div class="num">6</div><div class="lbl">Tickets</div></div>
    <div class="sc"><div class="num">7</div><div class="lbl">Endpoints</div></div>
    <div class="sc"><div class="num" id="live-reward">&#8212;</div><div class="lbl">Last Reward</div></div>
  </div>

  <div class="card">
    <h2>&#128193; Available Tasks</h2>
    <div class="tgrid">
      <div class="tc">
        <div><h3>Task 1 &#8212; Ticket Categorization</h3><p>Classify: billing | technical | general</p></div>
        <span class="diff easy">EASY</span>
      </div>
      <div class="tc">
        <div><h3>Task 2 &#8212; Category + Priority</h3><p>Classify + priority: low | medium | high</p></div>
        <span class="diff med">MEDIUM</span>
      </div>
      <div class="tc">
        <div><h3>Task 3 &#8212; Full Ticket Triage</h3><p>Classify + prioritize + write reply (min 10 words)</p></div>
        <span class="diff hard">HARD</span>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>&#129514; Try It Live</h2>

    <div class="lbl">Step 1 &#8212; Choose a task, then click RESET</div>
    <select id="task-select">
      <option value="task1_categorize">Task 1 &#8212; Categorize (Easy)</option>
      <option value="task2_prioritize">Task 2 &#8212; Category + Priority (Medium)</option>
      <option value="task3_full_triage">Task 3 &#8212; Full Triage (Hard)</option>
    </select>
    <button class="btn" id="reset-btn">&#128260; RESET &#8212; Get a Random Ticket</button>
    <div class="rlbl">Ticket received from /reset:</div>
    <div class="rbox" id="reset-box">&#9889; Click RESET above to get a ticket...</div>

    <div class="lbl" style="margin-top:16px">Step 2 &#8212; Edit your answer if needed, then click STEP</div>
    <textarea id="action-input">{ "category": "billing" }</textarea>
    <button class="btn" id="step-btn">&#9889; STEP &#8212; Submit Answer and Get Score</button>
    <div class="rlbl">Result from /step:</div>
    <div class="rbox" id="step-box">&#128260; Click RESET first, then STEP.</div>

    <div id="reward-wrap" style="display:none;margin-top:14px">
      <div class="lbl">Your Score (0.0 = wrong, 1.0 = perfect)</div>
      <div class="rbar-wrap"><div class="rbar" id="rbar"></div></div>
      <div class="rtxt" id="rtxt"></div>
    </div>

    <div class="lbl" style="margin-top:14px">Debug log (shows what is happening behind the scenes):</div>
    <div class="debug" id="debug-log">Waiting for action...</div>
  </div>

  <div class="card">
    <h2>&#128299; API Endpoints</h2>
    <table>
      <tr><th>Method</th><th>Endpoint</th><th>What it does</th></tr>
      <tr><td><span class="m get">GET</span></td><td>/</td><td>This dashboard</td></tr>
      <tr><td><span class="m post">POST</span></td><td>/reset</td><td>Get a new ticket to solve</td></tr>
      <tr><td><span class="m post">POST</span></td><td>/step</td><td>Submit answer, receive reward</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/state</td><td>Current environment state</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/tasks</td><td>All 3 tasks and schemas</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/grader</td><td>Last episode score</td></tr>
      <tr><td><span class="m get">GET</span></td><td>/baseline</td><td>Run baseline agent on all tasks</td></tr>
    </table>
    <br/>
    <a href="/docs" target="_blank">&#128214; Open Swagger API Docs &#8594;</a>
  </div>

</div>

<footer>
  Built for OpenEnv Round 1 &nbsp;|&nbsp;
  <a href="/docs" target="_blank">API Docs</a> &nbsp;|&nbsp;
  <a href="/tasks" target="_blank">Tasks JSON</a>
</footer>

<script>
(function() {

  // ---- Helpers ----
  function dbg(msg) {
    var el = document.getElementById("debug-log");
    if (el) {
      var t = new Date().toLocaleTimeString();
      el.textContent = "[" + t + "] " + msg + "\\n" + el.textContent;
    }
    console.log(msg);
  }

  function setBox(id, text, cls) {
    var el = document.getElementById(id);
    if (!el) { dbg("ERROR: element #" + id + " not found"); return; }
    el.textContent = text;
    el.className = "rbox" + (cls ? " " + cls : "");
  }

  function getBase() {
    return window.location.protocol + "//" + window.location.host;
  }

  var SCHEMAS = {
    "task1_categorize": '{ "category": "billing" }',
    "task2_prioritize": '{ "category": "billing", "priority": "high" }',
    "task3_full_triage": '{ "category": "billing", "priority": "high", "reply": "Thank you for contacting us. We will resolve your issue as soon as possible." }'
  };

  // ---- Reset ----
  function doReset() {
    var taskEl = document.getElementById("task-select");
    var taskId = taskEl ? taskEl.value : "task1_categorize";
    var base   = getBase();
    var url    = base + "/reset";

    dbg("RESET clicked. task=" + taskId + " url=" + url);
    setBox("reset-box", "Loading... sending request to " + url, "loading");
    setBox("step-box", "Waiting for reset to complete first...", "");
    document.getElementById("reward-wrap").style.display = "none";

    // Update action schema hint
    if (SCHEMAS[taskId]) {
      document.getElementById("action-input").value = SCHEMAS[taskId];
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json");
    xhr.timeout = 20000;

    xhr.onreadystatechange = function() {
      dbg("XHR state=" + xhr.readyState + " status=" + xhr.status);
    };

    xhr.onload = function() {
      dbg("RESET response: status=" + xhr.status + " len=" + xhr.responseText.length);
      if (xhr.status === 200) {
        try {
          var data = JSON.parse(xhr.responseText);
          setBox("reset-box", JSON.stringify(data, null, 2), "ok");
          dbg("RESET OK. ticket=" + (data.observation ? data.observation.ticket_id : "?"));
        } catch(e) {
          setBox("reset-box", "JSON parse error:\\n" + e.message + "\\n\\nRaw: " + xhr.responseText, "err");
          dbg("RESET parse error: " + e.message);
        }
      } else {
        setBox("reset-box", "HTTP " + xhr.status + " error:\\n" + xhr.responseText, "err");
        dbg("RESET HTTP error: " + xhr.status);
      }
    };

    xhr.onerror = function() {
      setBox("reset-box", "NETWORK ERROR\\nCould not reach: " + url + "\\nCheck if the server is running.", "err");
      dbg("RESET network error");
    };

    xhr.ontimeout = function() {
      setBox("reset-box", "TIMEOUT after 20 seconds\\nServer did not respond.", "err");
      dbg("RESET timeout");
    };

    try {
      var body = JSON.stringify({ "task_id": taskId });
      dbg("Sending: " + body);
      xhr.send(body);
    } catch(e) {
      setBox("reset-box", "Send error: " + e.message, "err");
      dbg("RESET send error: " + e.message);
    }
  }

  // ---- Step ----
  function doStep() {
    var raw  = document.getElementById("action-input").value.trim();
    var base = getBase();
    var url  = base + "/step";
    var action;

    dbg("STEP clicked. url=" + url);

    try {
      action = JSON.parse(raw);
      dbg("Action parsed OK: " + JSON.stringify(action));
    } catch(e) {
      setBox("step-box", "YOUR JSON IS INVALID!\\n\\nFix it to look like:\\n{ \\"category\\": \\"billing\\" }\\n\\nError: " + e.message, "err");
      dbg("STEP: JSON parse error: " + e.message);
      return;
    }

    setBox("step-box", "Loading... sending to " + url, "loading");

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json");
    xhr.timeout = 20000;

    xhr.onload = function() {
      dbg("STEP response: status=" + xhr.status + " len=" + xhr.responseText.length);
      if (xhr.status === 200) {
        try {
          var data = JSON.parse(xhr.responseText);

          if (data.error) {
            setBox("step-box", "Server error: " + data.error + "\\n\\nPlease click RESET first!", "err");
            dbg("STEP server error: " + data.error);
            return;
          }

          setBox("step-box", JSON.stringify(data, null, 2), "ok");

          if (data.reward !== undefined) {
            var r = parseFloat(data.reward);
            document.getElementById("reward-wrap").style.display = "block";
            document.getElementById("rbar").style.width = (r * 100) + "%";
            document.getElementById("live-reward").textContent = r;

            var rtxt = document.getElementById("rtxt");
            if (r >= 0.8) {
              rtxt.textContent = "SCORE: " + r + " / 1.0   Excellent! Correct answer!";
              rtxt.className = "rtxt good";
            } else if (r >= 0.4) {
              rtxt.textContent = "SCORE: " + r + " / 1.0   Partial credit. Some fields correct.";
              rtxt.className = "rtxt mid";
            } else {
              rtxt.textContent = "SCORE: " + r + " / 1.0   Wrong answer. Click RESET and try again.";
              rtxt.className = "rtxt bad";
            }
            dbg("STEP OK. reward=" + r);
          }
        } catch(e) {
          setBox("step-box", "JSON parse error:\\n" + e.message + "\\n\\nRaw: " + xhr.responseText, "err");
          dbg("STEP parse error: " + e.message);
        }
      } else {
        setBox("step-box", "HTTP " + xhr.status + " error:\\n" + xhr.responseText, "err");
        dbg("STEP HTTP error: " + xhr.status);
      }
    };

    xhr.onerror = function() {
      setBox("step-box", "NETWORK ERROR\\nCould not reach: " + url, "err");
      dbg("STEP network error");
    };

    xhr.ontimeout = function() {
      setBox("step-box", "TIMEOUT after 20 seconds.", "err");
      dbg("STEP timeout");
    };

    try {
      var body = JSON.stringify({ "action": action });
      dbg("Sending: " + body);
      xhr.send(body);
    } catch(e) {
      setBox("step-box", "Send error: " + e.message, "err");
      dbg("STEP send error: " + e.message);
    }
  }

  // ---- Wire up buttons AFTER DOM loads ----
  function init() {
    dbg("Page loaded. base=" + getBase());

    var rb = document.getElementById("reset-btn");
    var sb = document.getElementById("step-btn");

    if (rb) {
      rb.addEventListener("click", doReset);
      dbg("Reset button wired OK");
    } else {
      dbg("ERROR: reset-btn not found in DOM");
    }

    if (sb) {
      sb.addEventListener("click", doStep);
      dbg("Step button wired OK");
    } else {
      dbg("ERROR: step-btn not found in DOM");
    }
  }

  // Run init when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
</script>

</body>
</html>"""


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
        {"task_id": t["task_id"], "name": t["name"],
         "description": t["description"], "difficulty": t["difficulty"],
         "action_schema": t["action_schema"]}
        for t in TASKS
    ]

@app.get("/grader")
def grader():
    s = env.state()
    return {"task_id": s["task_id"], "last_reward": s["last_reward"], "done": s["done"]}

@app.get("/baseline")
def baseline():
    import inference as inf
    scores = inf.run_inference()
    return {"baseline_scores": scores}