from flask import Flask, render_template_string, jsonify, request
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memory.db import SQLiteAdapter
from memory.episodic import EpisodicMemory

app = Flask(__name__)
db_adapter = SQLiteAdapter()
global_workflow = None
global_memory = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Swarm Playground</title>
    <style>
        body { 
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #090d16, #0f172a, #111827); 
            color: #f3f4f6;
            padding: 20px; 
            margin: 0;
            min-height: 100vh;
        }
        .container { max-width: 1050px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 25px; }
        h1 { color: #38bdf8; font-weight: 300; font-size: 2.4rem; margin-bottom: 4px; letter-spacing: -0.02em; }
        p.subtitle { color: #9ca3af; margin-top: 0; font-size: 0.95rem; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
        
        .actors-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 25px;
        }
        .actor-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            padding: 12px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            text-align: center;
            transition: all 0.2s;
        }
        .actor-card.active { border-color: #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }
        .actor-name { font-weight: 600; font-size: 0.85rem; color: #e5e7eb; margin-bottom: 2px; }
        .actor-role { font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; margin-bottom: 6px; }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge.idle { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }
        .badge.active { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }

        .control-panel {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(12px);
            padding: 20px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 25px;
        }
        .task-tabs { display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }
        .tab-btn {
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(0,0,0,0.3);
            color: #9ca3af;
            cursor: pointer;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .tab-btn.active { background: #38bdf8; color: #090d16; border-color: #38bdf8; }
        
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        textarea, input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            background: rgba(17, 24, 39, 0.8);
            color: #fff;
            font-family: inherit;
            font-size: 0.95rem;
            outline: none;
        }
        textarea { height: 60px; resize: vertical; }
        button.action-btn {
            padding: 12px 24px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(135deg, #38bdf8, #0284c7);
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        button.action-btn:hover { box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3); }

        .glass-card { 
            background: rgba(255, 255, 255, 0.03);
            padding: 16px; 
            margin: 12px 0; 
            border-radius: 12px; 
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .meta { color: #6b7280; font-size: 0.8em; margin-bottom: 6px; }
        .role { color: #f43f5e; font-weight: 700; }
        .content { font-family: monospace; font-size: 0.92rem; line-height: 1.5; color: #e5e7eb; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Autonomous Swarm Playground</h1>
            <p class="subtitle">Live P2P Agent Chat, EvolvOS Skill Synthesis & Episodic Memory Graph</p>
        </header>

        <!-- Live Swarm Nodes -->
        <div class="actors-grid" id="actorsGrid"></div>

        <!-- Task & Chat Dispatcher -->
        <div class="control-panel">
            <div class="task-tabs">
                <button class="tab-btn active" onclick="setTaskType('chat')">💬 Live P2P Agent Chat</button>
                <button class="tab-btn" onclick="setTaskType('evolve')">🧬 EvolvOS Skill Synthesis</button>
                <button class="tab-btn" onclick="setTaskType('code')">💻 Code Sandbox</button>
                <button class="tab-btn" onclick="setTaskType('reasoning')">🧠 Prompt Reasoning</button>
            </div>

            <!-- Chat Panel Fields -->
            <div id="chatFields" class="input-group">
                <input type="text" id="chatSender" placeholder="Sender Agent (e.g. Agent-Alpha)" value="Agent-Alpha" style="max-width: 180px;" />
                <input type="text" id="chatRecipient" placeholder="Recipient Agent (e.g. Agent-Beta)" value="Agent-Beta" style="max-width: 180px;" />
                <input type="text" id="chatText" placeholder="Message content..." />
            </div>

            <!-- EvolvOS Fields -->
            <div id="evolveFields" style="display:none;">
                <div class="input-group">
                    <input type="text" id="skillName" placeholder="Skill Name (e.g. calculate_entropy)" style="max-width: 250px;" />
                    <input type="text" id="skillAssertion" placeholder="Assertion (e.g. assert calculate_entropy('abc') > 0)" />
                </div>
                <div class="input-group">
                    <textarea id="skillCode" placeholder="Python Code Template (e.g. def calculate_entropy(s):\n    import math\n    return len(set(s)) * math.log(len(s)))"></textarea>
                </div>
            </div>

            <!-- Generic Code / Prompt Fields -->
            <div id="genericFields" style="display:none;" class="input-group">
                <textarea id="taskData" placeholder="Payload content..."></textarea>
            </div>

            <div class="input-group" style="margin-top: 15px;">
                <button class="action-btn" onclick="dispatchTask()">Dispatch to Swarm</button>
                <input type="text" id="searchQuery" placeholder="Search episodic memory triplets..." onkeyup="if(event.key==='Enter') searchMemory()" />
                <button style="background: #374151;" class="action-btn" onclick="searchMemory()">Search</button>
            </div>
        </div>

        <!-- Live Swarm Memory Feed -->
        <div id="feed"></div>
    </div>

    <script>
        let currentTaskType = 'chat';

        function setTaskType(type) {
            currentTaskType = type;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('chatFields').style.display = type === 'chat' ? 'flex' : 'none';
            document.getElementById('evolveFields').style.display = type === 'evolve' ? 'block' : 'none';
            document.getElementById('genericFields').style.display = (type === 'code' || type === 'reasoning') ? 'flex' : 'none';
            
            const area = document.getElementById('taskData');
            if (type === 'code') area.placeholder = "Enter Python snippet (e.g. import math; print(math.factorial(10)))";
            else if (type === 'reasoning') area.placeholder = "Enter reasoning prompt query...";
        }

        async function fetchActors() {
            try {
                const res = await fetch('/api/actors');
                const actors = await res.json();
                const grid = document.getElementById('actorsGrid');
                grid.innerHTML = '';
                actors.forEach(a => {
                    const card = document.createElement('div');
                    card.className = `actor-card ${a.state === 'active' ? 'active' : ''}`;
                    card.innerHTML = `
                        <div class="actor-name">${a.name}</div>
                        <div class="actor-role">${a.role}</div>
                        <span class="badge ${a.state}">${a.state}</span>
                    `;
                    grid.appendChild(card);
                });
            } catch(e){}
        }

        async function fetchFeed() {
            try {
                const res = await fetch('/api/memory');
                renderFeed(await res.json());
            } catch(e){}
        }

        async function dispatchTask() {
            let body = { type: currentTaskType };
            if (currentTaskType === 'chat') {
                body.sender = document.getElementById('chatSender').value.trim() || 'Agent-Alpha';
                body.recipient = document.getElementById('chatRecipient').value.trim() || 'Agent-Beta';
                body.text = document.getElementById('chatText').value.trim();
                if (!body.text) return alert("Enter chat text.");
            } else if (currentTaskType === 'evolve') {
                body.skill_name = document.getElementById('skillName').value.trim() || 'custom_skill';
                body.code = document.getElementById('skillCode').value.trim();
                body.assertion = document.getElementById('skillAssertion').value.trim();
                if (!body.code) return alert("Enter Python code template.");
            } else if (currentTaskType === 'code') {
                body.code = document.getElementById('taskData').value.trim();
            } else if (currentTaskType === 'reasoning') {
                body.query = document.getElementById('taskData').value.trim();
            }

            try {
                const res = await fetch('/api/dispatch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const out = await res.json();
                alert(out.message || "Dispatched");
                fetchFeed();
            } catch(e) { alert("Dispatch error"); }
        }

        async function searchMemory() {
            const q = document.getElementById('searchQuery').value.trim();
            if (!q) return fetchFeed();
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                renderFeed(await res.json());
            } catch(e){}
        }

        function renderFeed(data) {
            const container = document.getElementById('feed');
            container.innerHTML = '';
            if (!data || data.length === 0) {
                container.innerHTML = '<div style="text-align:center; color:#6b7280; padding:20px;">No swarm memory events yet.</div>';
                return;
            }
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'glass-card';
                let role = item.role || item[2] || 'Swarm Event';
                let time = item.timestamp ? new Date(item.timestamp * 1000).toLocaleString() : (item[1] || '');
                let content = item.content || item[3] || '';
                
                div.innerHTML = `
                    <div class="meta"><span class="role">${role}</span> | ${time}</div>
                    <div class="content">${content}</div>
                `;
                container.appendChild(div);
            });
        }

        setInterval(() => { fetchActors(); fetchFeed(); }, 3000);
        fetchActors();
        fetchFeed();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/actors')
def api_actors():
    if global_workflow:
        return jsonify(global_workflow.get_actors_status())
    return jsonify([])

@app.route('/api/memory')
def api_memory():
    try:
        results = db_adapter.select(limit=50)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dispatch', methods=['POST'])
def api_dispatch():
    data = request.get_json() or {}
    task_type = data.get('type', 'chat')
    
    if global_workflow and global_workflow.loop:
        import asyncio
        asyncio.run_coroutine_threadsafe(
            global_workflow.dispatch_user_task(task_type, data), 
            global_workflow.loop
        )
        return jsonify({"status": "success", "message": f"Dispatched '{task_type}' task to Swarm."})
    return jsonify({"error": "Workflow loop inactive."}), 500

@app.route('/api/infer_sync', methods=['POST'])
def api_infer_sync():
    data = request.get_json() or {}
    prompt = data.get('prompt', '')
    import subprocess
    try:
        out = subprocess.check_output([
            '/data/data/com.termux/files/home/Projects/local/native_ai_engine/build/native_ai_engine', 
            '-m', '/data/data/com.termux/files/home/models/phi-3-mini-q4.gguf', 
            '-p', prompt, 
            '-n', '256'
        ], text=True)
        
        # Filter out C++ logs so we only return the actual model answer
        clean_lines = []
        for line in out.split('\n'):
            line = line.strip()
            if line and not line.startswith('[INFO]') and not line.startswith('[RawModel]'):
                clean_lines.append(line)
                
        return jsonify({"result": '\n'.join(clean_lines)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if not query:
        return api_memory()
    if global_memory:
        events = global_memory.retrieve_events(query, limit=15)
        return jsonify([e.to_dict() for e in events])
    else:
        results = db_adapter.select(limit=50)
        filtered = [r for r in results if query.lower() in str(r[3]).lower()]
        return jsonify(filtered)

def run_dashboard(workflow=None, memory=None, port=5000):
    global global_workflow, global_memory
    global_workflow = workflow
    global_memory = memory
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_dashboard()
