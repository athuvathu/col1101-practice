#!/usr/bin/env python3
"""
vpl_server.py - Full In-Browser Virtual Programming Lab (VPL) Local Server
COL1101 Diwali 2026 Programming Quiz Practice Suite

Includes:
- Authentic Ace Editor with Python syntax highlighting
- Bracket auto-pairing (), [], {}, "", ''
- Auto-indentation after colons & soft tabs (4 spaces)
- Live two-way file sync with student_code.py on disk
- One-click [Run] and [Evaluate] buttons with Ctrl+Enter and Ctrl+S shortcuts
- Real-time VPL terminal evaluation output with Grade parsing
- 90-minute countdown stopwatch with Space/P pause/resume
"""

import sys
import os
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = BASE_DIR / "portal" / "vendor"

PROBLEMS = {
    "exam1": {
        "q1": {
            "title": "Problem 1: Sliding Window Max XOR (Binary Trie)",
            "marks": 40,
            "target_time": "35 min",
            "dir": BASE_DIR / "exam1" / "Q1_Trie_Frequency_Filter",
        },
        "q2": {
            "title": "Problem 2: Running Quantile Monitor (Dual Heaps)",
            "marks": 60,
            "target_time": "55 min",
            "dir": BASE_DIR / "exam1" / "Q2_Augmented_Order_BST",
        }
    },
    "exam2": {
        "q1": {
            "title": "Problem 1: Limit Order Book Crossing Engine (Standard BST)",
            "marks": 40,
            "target_time": "35 min",
            "dir": BASE_DIR / "exam2" / "Q1_Dual_Heap_Scheduler",
        },
        "q2": {
            "title": "Problem 2: Longest Divisible Subarray (FastHashTable)",
            "marks": 60,
            "target_time": "55 min",
            "dir": BASE_DIR / "exam2" / "Q2_Cuckoo_Linear_Hash",
        }
    }
}


class VPLHandler(BaseHTTPRequestHandler):

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status=200)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_vpl_html()
        elif path.startswith("/vendor/"):
            self._serve_vendor_file(path[len("/vendor/"):])
        elif path == "/api/problem":
            self._handle_get_problem(parse_qs(parsed.query))
        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"Not Found")

    def _serve_vendor_file(self, filename: str):
        try:
            file_path = (VENDOR_DIR / filename).resolve()
            if not str(file_path).startswith(str(VENDOR_DIR.resolve())) or not file_path.is_file():
                self._set_headers("text/plain", 404)
                self.wfile.write(b"Vendor file not found")
                return

            ext = file_path.suffix.lower()
            mime_map = {
                ".js": "application/javascript",
                ".css": "text/css",
                ".woff2": "font/woff2",
                ".woff": "font/woff",
                ".ttf": "font/ttf",
                ".html": "text/html",
                ".json": "application/json",
            }
            content_type = mime_map.get(ext, "application/octet-stream")
            self._set_headers(content_type, 200)
            self.wfile.write(file_path.read_bytes())
        except Exception as e:
            self._set_headers("text/plain", 500)
            self.wfile.write(str(e).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        data = json.loads(body) if body else {}

        if path == "/api/save":
            self._handle_save(data)
        elif path == "/api/evaluate":
            self._handle_evaluate(data)
        elif path == "/api/run":
            self._handle_run(data)
        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"Not Found")

    def _handle_get_problem(self, query):
        exam = query.get("exam", ["exam1"])[0]
        q = query.get("q", ["q1"])[0]

        if exam not in PROBLEMS or q not in PROBLEMS[exam]:
            self._set_headers(status=400)
            self.wfile.write(json.dumps({"error": "Invalid exam/q"}).encode("utf-8"))
            return

        info = PROBLEMS[exam][q]
        q_dir = info["dir"]

        student_code = (q_dir / "student_code.py").read_text(encoding="utf-8") if (q_dir / "student_code.py").exists() else ""
        common_code = (q_dir / "common.py").read_text(encoding="utf-8") if (q_dir / "common.py").exists() else ""
        readme_text = (q_dir / "README.md").read_text(encoding="utf-8") if (q_dir / "README.md").exists() else ""

        payload = {
            "exam": exam,
            "q": q,
            "title": info["title"],
            "marks": info["marks"],
            "target_time": info["target_time"],
            "student_code": student_code,
            "common_code": common_code,
            "description": readme_text
        }
        self._set_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _handle_save(self, data):
        exam = data.get("exam", "exam1")
        q = data.get("q", "q1")
        code = data.get("code", "")

        if exam in PROBLEMS and q in PROBLEMS[exam]:
            q_dir = PROBLEMS[exam][q]["dir"]
            (q_dir / "student_code.py").write_text(code, encoding="utf-8")
            self._set_headers()
            self.wfile.write(json.dumps({"status": "saved"}).encode("utf-8"))
        else:
            self._set_headers(status=400)
            self.wfile.write(json.dumps({"error": "Invalid target"}).encode("utf-8"))

    def _handle_evaluate(self, data):
        exam = data.get("exam", "exam1")
        q = data.get("q", "q1")
        code = data.get("code", None)

        if exam not in PROBLEMS or q not in PROBLEMS[exam]:
            self._set_headers(status=400)
            self.wfile.write(json.dumps({"error": "Invalid target"}).encode("utf-8"))
            return

        q_dir = PROBLEMS[exam][q]["dir"]
        if code is not None:
            (q_dir / "student_code.py").write_text(code, encoding="utf-8")

        # Run test suite
        proc = subprocess.run(
            [sys.executable, str(q_dir / "test_suite.py"), "student_code"],
            cwd=str(q_dir),
            capture_output=True,
            text=True
        )

        output = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
        self._set_headers()
        self.wfile.write(json.dumps({
            "output": output,
            "exit_code": proc.returncode
        }).encode("utf-8"))

    def _handle_run(self, data):
        exam = data.get("exam", "exam1")
        q = data.get("q", "q1")
        code = data.get("code", None)
        q_dir = PROBLEMS[exam][q]["dir"]

        if code is not None:
            (q_dir / "student_code.py").write_text(code, encoding="utf-8")

        # Run visible sample tests with live debug prints
        sample_script = q_dir / "sample_tests.py"
        if sample_script.exists():
            check_cmd = [sys.executable, str(sample_script), "student_code"]
        else:
            check_cmd = [sys.executable, "-c", "import student_code; print('Syntax & imports OK!')"]
        proc = subprocess.run(check_cmd, cwd=str(q_dir), capture_output=True, text=True)
        out = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
        self._set_headers()
        self.wfile.write(json.dumps({"output": out, "exit_code": proc.returncode}).encode("utf-8"))

    def _serve_vpl_html(self):
        self._set_headers("text/html", 200)
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>IIT Delhi VPL Exam Environment — COL1101</title>
  <!-- Load Ace Editor, Marked & KaTeX locally with CDN fallback -->
  <link rel="stylesheet" href="/vendor/katex.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
  <script src="/vendor/katex.min.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js'"></script>
  <script src="/vendor/auto-render.min.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js'"></script>
  <script src="/vendor/ace.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ace.js'"></script>
  <script src="/vendor/mode-python.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/mode-python.js'"></script>
  <script src="/vendor/mode-markdown.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/mode-markdown.js'"></script>
  <script src="/vendor/theme-tomorrow_night.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-tomorrow_night.js'"></script>
  <script src="/vendor/theme-monokai.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-monokai.js'"></script>
  <script src="/vendor/theme-dracula.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-dracula.js'"></script>
  <script src="/vendor/theme-gruvbox.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-gruvbox.js'"></script>
  <script src="/vendor/theme-one_dark.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-one_dark.js'"></script>
  <script src="/vendor/theme-solarized_dark.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-solarized_dark.js'"></script>
  <script src="/vendor/theme-github.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-github.js'"></script>
  <script src="/vendor/theme-solarized_light.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/theme-solarized_light.js'"></script>
  <script src="/vendor/marked.min.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/marked/11.1.1/marked.min.js'"></script>

  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', Menlo, monospace;
      background: #0d1117;
      color: #c9d1d9;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      font-size: 13px;
    }

    /* Top Banner / Navbar */
    header {
      background: #161b22;
      border-bottom: 1px solid #30363d;
      padding: 8px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 48px;
      flex-shrink: 0;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand h1 {
      font-size: 13.5px;
      color: #58a6ff;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .exam-select {
      background: #0d1117;
      color: #c9d1d9;
      border: 1px solid #30363d;
      padding: 4px 8px;
      border-radius: 4px;
      font-family: inherit;
      font-size: 12px;
      cursor: pointer;
    }

    .toolbar-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn {
      background: #21262d;
      color: #c9d1d9;
      border: 1px solid #30363d;
      padding: 5px 12px;
      border-radius: 4px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: background 0.15s;
    }
    .btn:hover { background: #30363d; }
    .btn-run { background: #1f6feb; border-color: #388bfd; color: #fff; }
    .btn-run:hover { background: #388bfd; }
    .btn-eval { background: #238636; border-color: #2ea043; color: #fff; }
    .btn-eval:hover { background: #2ea043; }

    .timer-pill {
      background: #0d1117;
      border: 1px solid #30363d;
      padding: 4px 10px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 13px;
      color: #58a6ff;
      letter-spacing: 0.5px;
      cursor: pointer;
      user-select: none;
    }
    .timer-pill.paused { color: #d29922; }

    .kbd {
      background: #21262d;
      border: 1px solid #30363d;
      font-size: 10px;
      padding: 1px 4px;
      border-radius: 3px;
      color: #8b949e;
    }

    /* Main Workspace Grid */
    .workspace {
      display: flex;
      flex: 1;
      overflow: hidden;
    }

    /* Left: Problem Handout */
    .left-panel {
      width: 44%;
      background: #0d1117;
      border-right: 1px solid #30363d;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .panel-header {
      background: #161b22;
      border-bottom: 1px solid #30363d;
      padding: 6px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
      height: 38px;
      flex-shrink: 0;
    }
    .question-tabs {
      display: flex;
      gap: 4px;
    }
    .q-btn {
      background: transparent;
      border: 1px solid transparent;
      color: #8b949e;
      padding: 4px 10px;
      border-radius: 4px;
      font-family: inherit;
      font-size: 11.5px;
      cursor: pointer;
    }
    .q-btn.active {
      background: #0d1117;
      border-color: #30363d;
      color: #58a6ff;
      font-weight: 700;
    }
    .problem-content {
      flex: 1;
      padding: 16px 20px;
      overflow-y: auto;
      line-height: 1.6;
      color: #c9d1d9;
    }
    .problem-content h1 { font-size: 16px; color: #f0f6fc; margin: 0 0 12px 0; border-bottom: 1px solid #21262d; padding-bottom: 8px; }
    .problem-content h2 { font-size: 14px; color: #79c0ff; margin: 16px 0 8px 0; }
    .problem-content h3 { font-size: 13px; color: #d2a8ff; margin: 14px 0 6px 0; }
    .problem-content p { margin-bottom: 10px; }
    .problem-content ul, .problem-content ol { margin: 8px 0 12px 20px; }
    .problem-content li { margin-bottom: 4px; }
    .problem-content pre {
      background: #161b22;
      padding: 12px;
      border-radius: 4px;
      overflow-x: auto;
      margin: 10px 0 14px 0;
      border: 1px solid #30363d;
      font-size: 12px;
      line-height: 1.45;
    }
    .problem-content code {
      background: #161b22;
      padding: 2px 4px;
      border-radius: 3px;
      color: #79c0ff;
      font-size: 12px;
    }

    /* Right: Code Editor & VPL Terminal */
    .right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: #0d1117;
      min-width: 0;
    }
    .editor-tabs {
      display: flex;
      background: #161b22;
      border-bottom: 1px solid #30363d;
      padding: 0 8px;
      height: 38px;
      align-items: center;
      flex-shrink: 0;
      overflow-x: auto;
      overflow-y: hidden;
      white-space: nowrap;
    }
    .file-tab {
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: #8b949e;
      padding: 8px 14px;
      font-family: inherit;
      font-size: 12px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .file-tab.active {
      color: #f0f6fc;
      border-bottom-color: #f78166;
      font-weight: 600;
    }
    .readonly-badge {
      font-size: 9px;
      background: #21262d;
      padding: 1px 4px;
      border-radius: 2px;
      color: #8b949e;
    }

    /* Ace Editor Host */
    #ace-editor {
      flex: 1;
      width: 100%;
      height: 100%;
      font-size: 13px;
      line-height: 1.5;
    }

    /* Bottom Terminal */
    .terminal-panel {
      height: 240px;
      background: #010409;
      border-top: 1px solid #30363d;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .terminal-header {
      background: #161b22;
      padding: 6px 12px;
      font-size: 11px;
      color: #8b949e;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #21262d;
      height: 28px;
      flex-shrink: 0;
    }
    .terminal-output {
      flex: 1;
      padding: 10px 14px;
      color: #58a6ff;
      font-size: 12px;
      line-height: 1.5;
      overflow-y: auto;
      white-space: pre-wrap;
      font-family: inherit;
    }
    .score-banner {
      display: inline-block;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 3px;
      margin-left: 8px;
    }
    .score-pass { background: #111a13; border: 1px solid #238636; color: #3fb950; }
    .score-fail { background: #261113; border: 1px solid #da3633; color: #f85149; }

    /* Editor Quick Settings (Theme & Font Size) */
    .editor-quick-settings {
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-right: 8px;
      flex-shrink: 0;
    }
    #save-status {
      font-size: 11px;
      color: #8b949e;
      white-space: nowrap;
      min-width: 60px;
    }
    .setting-label {
      font-size: 11px;
      color: #8b949e;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .setting-select {
      background: #0d1117;
      color: #c9d1d9;
      border: 1px solid #30363d;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: inherit;
      font-size: 11px;
      cursor: pointer;
      outline: none;
    }
    .setting-select:hover, .setting-select:focus {
      border-color: #58a6ff;
    }
    .btn-theme {
      background: #21262d;
      border-color: #30363d;
      color: #c9d1d9;
      font-size: 11px;
      padding: 4px 8px;
    }
    .btn-theme:hover {
      background: #30363d;
      color: #58a6ff;
    }

    /* Light Theme Overrides */
    body.light-theme {
      background: #f6f8fa;
      color: #24292f;
    }
    body.light-theme header {
      background: #ffffff;
      border-bottom: 1px solid #d0d7de;
    }
    body.light-theme .brand h1 {
      color: #0969da;
    }
    body.light-theme .exam-select {
      background: #ffffff;
      color: #24292f;
      border: 1px solid #d0d7de;
    }
    body.light-theme .btn {
      background: #f6f8fa;
      color: #24292f;
      border: 1px solid #d0d7de;
    }
    body.light-theme .btn:hover {
      background: #eaeef2;
    }
    body.light-theme .btn-run {
      background: #0969da;
      border-color: #0969da;
      color: #fff;
    }
    body.light-theme .btn-run:hover {
      background: #0860ca;
    }
    body.light-theme .btn-eval {
      background: #1a7f37;
      border-color: #1a7f37;
      color: #fff;
    }
    body.light-theme .btn-eval:hover {
      background: #166e30;
    }
    body.light-theme .btn-reset {
      background: #f6f8fa;
      border-color: #d0d7de;
      color: #57606a;
    }
    body.light-theme .btn-reset:hover {
      background: #cf222e;
      border-color: #cf222e;
      color: #fff;
    }
    body.light-theme .btn-theme {
      background: #ffffff;
      border-color: #d0d7de;
      color: #24292f;
    }
    body.light-theme .timer-pill {
      background: #ffffff;
      border-color: #d0d7de;
      color: #24292f;
    }
    body.light-theme .left-panel {
      background: #f6f8fa;
      border-right: 1px solid #d0d7de;
    }
    body.light-theme .panel-header {
      background: #ffffff;
      border-bottom: 1px solid #d0d7de;
    }
    body.light-theme .q-btn {
      color: #57606a;
    }
    body.light-theme .q-btn.active {
      color: #0969da;
      background: #ddf4ff;
      border-color: #54aeff;
    }
    body.light-theme .problem-content {
      color: #24292f;
    }
    body.light-theme .problem-content h1,
    body.light-theme .problem-content h2,
    body.light-theme .problem-content h3 {
      color: #24292f;
      border-bottom-color: #d0d7de;
    }
    body.light-theme .problem-content code {
      background: #eaeef2;
      color: #24292f;
    }
    body.light-theme .problem-content pre {
      background: #f6f8fa;
      border: 1px solid #d0d7de;
      color: #24292f;
    }
    body.light-theme .right-panel {
      background: #ffffff;
    }
    body.light-theme .editor-tabs {
      background: #ffffff;
      border-bottom: 1px solid #d0d7de;
    }
    body.light-theme .file-tab {
      color: #57606a;
    }
    body.light-theme .file-tab.active {
      color: #24292f;
      border-bottom-color: #fd8c73;
    }
    body.light-theme .readonly-badge {
      background: #eaeef2;
      color: #57606a;
    }
    body.light-theme .setting-label {
      color: #57606a;
    }
    body.light-theme .setting-select {
      background: #ffffff;
      color: #24292f;
      border: 1px solid #d0d7de;
    }
    body.light-theme .terminal-panel {
      background: #ffffff;
      border-top: 1px solid #d0d7de;
    }
    body.light-theme .terminal-header {
      background: #ffffff;
      border-bottom: 1px solid #d0d7de;
      color: #24292f;
    }
    body.light-theme .terminal-output {
      background: #f6f8fa;
      color: #24292f;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <h1>IIT DELHI VPL &bull; COL1101</h1>
      <select id="exam-select" class="exam-select" onchange="onExamChange()">
        <option value="exam1">COL1101 Mock Exam 1 (Authentic 1.5-Hr)</option>
        <option value="exam2">COL1101 Mock Exam 2 (Alternative 1.5-Hr)</option>
      </select>
    </div>

    <div class="toolbar-actions">
      <div id="timer" class="timer-pill" onclick="toggleTimer()" title="Click or press Space to pause/resume">90:00 [Space]</div>
      <button class="btn btn-run" onclick="onRun()" title="Shortcut: Ctrl+R / Cmd+R">&#9654; Run Visible Tests (Debug) <span class="kbd">Ctrl+R</span></button>
      <button class="btn btn-eval" onclick="onEvaluate()" title="Shortcut: Ctrl+Enter / Cmd+Enter">&#9733; Evaluate (VPL Test) <span class="kbd">Ctrl+Enter</span></button>
      <button id="theme-toggle-btn" class="btn btn-theme" onclick="togglePortalTheme()" title="Toggle Dark/Light Mode">&#9681; Dark</button>
    </div>
  </header>

  <div class="workspace">
    <!-- Left: Handout -->
    <div class="left-panel">
      <div class="panel-header">
        <div class="question-tabs">
          <button id="q1-btn" class="q-btn active" onclick="switchQuestion('q1')">Question 1</button>
          <button id="q2-btn" class="q-btn" onclick="switchQuestion('q2')">Question 2</button>
        </div>
        <span id="q-meta" style="color: #3fb950; font-weight: 700;">40 Marks</span>
      </div>
      <div id="problem-desc" class="problem-content">Loading problem handout...</div>
    </div>

    <!-- Right: Code Editor & VPL Terminal -->
    <div class="right-panel">
      <div class="editor-tabs">
        <button id="tab-student" class="file-tab active" onclick="switchFileTab('student')">
          <span>student_code.py</span>
        </button>
        <button id="tab-common" class="file-tab" onclick="switchFileTab('common')">
          <span>common.py</span>
          <span class="readonly-badge">READONLY</span>
        </button>
        <button id="tab-readme" class="file-tab" onclick="switchFileTab('readme')">
          <span>README.md</span>
          <span class="readonly-badge">READONLY</span>
        </button>
        <div class="editor-quick-settings">
          <label class="setting-label">Theme:
            <select id="theme-select" class="setting-select" onchange="onThemeChange(this.value)" title="Change editor color theme">
              <optgroup label="Dark">
                <option value="tomorrow_night" selected>Tomorrow Night</option>
                <option value="monokai">Monokai</option>
                <option value="dracula">Dracula</option>
                <option value="gruvbox">Gruvbox</option>
                <option value="one_dark">One Dark</option>
                <option value="solarized_dark">Solarized Dark</option>
              </optgroup>
              <optgroup label="Light">
                <option value="github">GitHub Light</option>
                <option value="solarized_light">Solarized Light</option>
              </optgroup>
            </select>
          </label>
          <label class="setting-label">Font:
            <select id="font-size-select" class="setting-select" onchange="onFontSizeChange(this.value)" title="Change font size (Shortcut: Ctrl+= / Ctrl+-)">
              <option value="11">11px</option>
              <option value="12">12px</option>
              <option value="13" selected>13px</option>
              <option value="14">14px</option>
              <option value="15">15px</option>
              <option value="16">16px</option>
              <option value="18">18px</option>
              <option value="20">20px</option>
            </select>
          </label>
          <span id="save-status">Saved</span>
        </div>
      </div>

      <!-- Ace Editor Host -->
      <div id="ace-editor"></div>

      <!-- VPL Evaluation Console -->
      <div class="terminal-panel">
        <div class="terminal-header">
          <span>VPL EVALUATION CONSOLE <span id="grade-badge"></span></span>
          <span id="exec-status">Ready</span>
        </div>
        <div id="terminal" class="terminal-output">Press [Evaluate] or Ctrl+Enter to run the test suite on student_code.py.
Execution traces, test passes/fails, and official Grade :=>> <score> will appear here.</div>
      </div>
    </div>
  </div>

  <script>
    let currentExam = "exam1";
    let currentQ = "q1";
    let currentFileTab = "student";
    let problemData = {};
    let saveTimeout = null;
    let editor = null;

    // Theme & Font Size state persisted in localStorage
    const FONT_SIZES = [11, 12, 13, 14, 15, 16, 18, 20];
    let currentTheme = localStorage.getItem('col1101_editor_theme') || 'tomorrow_night';
    let currentFontSize = parseInt(localStorage.getItem('col1101_font_size') || '13', 10);
    if (!FONT_SIZES.includes(currentFontSize)) currentFontSize = 13;
    let currentPortalTheme = localStorage.getItem('col1101_portal_theme') || 'dark';

    function applyTheme(themeName) {
      currentTheme = themeName;
      if (editor) {
        editor.setTheme("ace/theme/" + themeName);
      }
      localStorage.setItem('col1101_editor_theme', themeName);
      const select = document.getElementById('theme-select');
      if (select && select.value !== themeName) {
        select.value = themeName;
      }
    }

    function onThemeChange(themeName) {
      applyTheme(themeName);
      if ((themeName === 'github' || themeName === 'solarized_light') && currentPortalTheme === 'dark') {
        applyPortalTheme('light');
      } else if (themeName !== 'github' && themeName !== 'solarized_light' && currentPortalTheme === 'light') {
        applyPortalTheme('dark');
      }
    }

    function applyFontSize(size) {
      currentFontSize = parseInt(size, 10);
      if (editor) {
        editor.setOption("fontSize", currentFontSize + "px");
      }
      const terminal = document.getElementById('terminal');
      if (terminal) {
        terminal.style.fontSize = Math.max(11, currentFontSize - 1) + "px";
      }
      localStorage.setItem('col1101_font_size', currentFontSize);
      const select = document.getElementById('font-size-select');
      if (select && parseInt(select.value, 10) !== currentFontSize) {
        select.value = currentFontSize;
      }
    }

    function onFontSizeChange(size) {
      applyFontSize(size);
    }

    function stepFontSize(delta) {
      let idx = FONT_SIZES.indexOf(currentFontSize);
      if (idx === -1) idx = 2;
      const nextIdx = Math.max(0, Math.min(FONT_SIZES.length - 1, idx + delta));
      applyFontSize(FONT_SIZES[nextIdx]);
    }

    function initPortalTheme() {
      applyPortalTheme(currentPortalTheme);
    }

    function applyPortalTheme(mode) {
      currentPortalTheme = mode;
      document.body.classList.toggle('light-theme', mode === 'light');
      localStorage.setItem('col1101_portal_theme', mode);
      const btn = document.getElementById('theme-toggle-btn');
      if (btn) {
        btn.innerHTML = mode === 'light' ? '&#9728; Light' : '&#9681; Dark';
      }
    }

    function togglePortalTheme() {
      const next = currentPortalTheme === 'dark' ? 'light' : 'dark';
      applyPortalTheme(next);
      if (next === 'light' && (currentTheme === 'tomorrow_night' || currentTheme === 'one_dark')) {
        applyTheme('github');
      } else if (next === 'dark' && currentTheme === 'github') {
        applyTheme('tomorrow_night');
      }
    }

    // Timer state
    let timeLeft = 90 * 60;
    let timerRunning = false;
    let timerInterval = null;

    function initAce() {
      editor = ace.edit("ace-editor");
      editor.setTheme("ace/theme/" + currentTheme);
      editor.session.setMode("ace/mode/python");
      editor.session.setUseWorker(false);

      // Bracket auto-pairing and typing ergonomics
      editor.setBehavioursEnabled(true);
      editor.setWrapBehavioursEnabled(true);

      editor.setOptions({
        fontSize: currentFontSize + "px",
        fontFamily: "'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', Menlo, monospace",
        tabSize: 4,
        useSoftTabs: true,
        showPrintMargin: false,
        highlightActiveLine: true,
        highlightSelectedWord: true,
        autoScrollEditorIntoView: true,
        enableBasicAutocompletion: false,
        enableLiveAutocompletion: false,
        enableSnippets: false
      });

      applyTheme(currentTheme);
      applyFontSize(currentFontSize);

      // Keyboard shortcuts
      editor.commands.addCommand({
        name: 'saveCode',
        bindKey: {win: 'Ctrl-S', mac: 'Command-S'},
        exec: function() { saveCode(); }
      });

      editor.commands.addCommand({
        name: 'evaluateCode',
        bindKey: {win: 'Ctrl-Enter', mac: 'Command-Enter'},
        exec: function() { onEvaluate(); }
      });

      editor.commands.addCommand({
        name: 'runCode',
        bindKey: {win: 'Ctrl-R', mac: 'Command-R'},
        exec: function() { onRun(); }
      });

      editor.commands.addCommand({
        name: 'increaseFontSize',
        bindKey: {win: 'Ctrl-=', mac: 'Command-='},
        exec: function() { stepFontSize(1); }
      });

      editor.commands.addCommand({
        name: 'decreaseFontSize',
        bindKey: {win: 'Ctrl--', mac: 'Command--'},
        exec: function() { stepFontSize(-1); }
      });

      editor.commands.addCommand({
        name: 'resetFontSize',
        bindKey: {win: 'Ctrl-0', mac: 'Command-0'},
        exec: function() { applyFontSize(13); }
      });

      editor.session.on('change', function() {
        if (currentFileTab === 'student') {
          problemData.student_code = editor.getValue();
          document.getElementById('save-status').textContent = 'Editing...';
          clearTimeout(saveTimeout);
          saveTimeout = setTimeout(saveCode, 400);
        }
      });
    }

    function renderDescription(markdown) {
      if (!markdown) {
        document.getElementById('problem-desc').innerHTML = '';
        return;
      }

      const mathBlocks = [];
      const mathInlines = [];

      // 1. Extract Display Math: $$...$$
      let cleaned = markdown.replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (match, math) => {
        const id = mathBlocks.length;
        if (window.katex) {
          try {
            mathBlocks.push(katex.renderToString(math.trim(), { displayMode: true, throwOnError: false }));
          } catch (e) {
            mathBlocks.push(match);
          }
        } else {
          mathBlocks.push(match);
        }
        return `%%%MATHBLOCK_${id}%%%`;
      });

      // 2. Extract Inline Math: $...$
      cleaned = cleaned.replace(/\\$([^\\$\\n]+?)\\$/g, (match, math) => {
        const id = mathInlines.length;
        if (window.katex) {
          try {
            mathInlines.push(katex.renderToString(math.trim(), { displayMode: false, throwOnError: false }));
          } catch (e) {
            mathInlines.push(match);
          }
        } else {
          mathInlines.push(match);
        }
        return `%%%MATHINLINE_${id}%%%`;
      });

      // 3. Parse Markdown
      let html = window.marked ? marked.parse(cleaned) : cleaned;

      // 4. Restore rendered Math
      html = html.replace(/%%%MATHBLOCK_(\\d+)%%%/g, (match, id) => mathBlocks[parseInt(id)] || match);
      html = html.replace(/%%%MATHINLINE_(\\d+)%%%/g, (match, id) => mathInlines[parseInt(id)] || match);

      document.getElementById('problem-desc').innerHTML = html;
      if (window.renderMathInElement) {
        try {
          renderMathInElement(document.getElementById('problem-desc'), {
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false}
            ],
            ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
          });
        } catch (e) {}
      }
    }

    async function loadProblem() {
      document.getElementById('exec-status').textContent = 'Loading...';
      const res = await fetch(`/api/problem?exam=${currentExam}&q=${currentQ}`);
      problemData = await res.json();

      document.getElementById('q-meta').textContent = `${problemData.marks} Marks (${problemData.target_time})`;
      
      // Render markdown with KaTeX protection
      renderDescription(problemData.description);

      renderEditorContent();
      document.getElementById('exec-status').textContent = 'Ready';
    }

    function renderEditorContent() {
      if (!editor) return;
      if (currentFileTab === 'student') {
        editor.setValue(problemData.student_code || "", -1);
        editor.setReadOnly(false);
        editor.session.setMode("ace/mode/python");
        editor.session.setUseWorker(false);
      } else if (currentFileTab === 'common') {
        editor.setValue(problemData.common_code || "", -1);
        editor.setReadOnly(true);
        editor.session.setMode("ace/mode/python");
        editor.session.setUseWorker(false);
      } else if (currentFileTab === 'readme') {
        editor.setValue(problemData.description || "", -1);
        editor.setReadOnly(true);
        editor.session.setMode("ace/mode/markdown");
        editor.session.setUseWorker(false);
      }
    }

    async function saveCode() {
      if (currentFileTab !== 'student' || !editor) return;
      document.getElementById('save-status').textContent = 'Saving...';
      await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exam: currentExam,
          q: currentQ,
          code: editor.getValue()
        })
      });
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      document.getElementById('save-status').textContent = `Saved (${timeStr})`;
    }

    async function onRun() {
      document.getElementById('exec-status').textContent = 'Running visible samples...';
      const terminal = document.getElementById('terminal');
      terminal.textContent = 'Executing visible sample tests with live debug prints...\\n';
      const gradeBadge = document.getElementById('grade-badge');
      gradeBadge.className = '';
      gradeBadge.textContent = '';

      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exam: currentExam, q: currentQ, code: editor.getValue() })
      });
      const data = await res.json();
      terminal.textContent = data.output;

      const sampleMatch = data.output.match(/SAMPLE RUN COMPLETE: (\\d+)\\/(\\d+) Cases Passed/);
      if (sampleMatch) {
        const passed = parseInt(sampleMatch[1]);
        const total = parseInt(sampleMatch[2]);
        gradeBadge.textContent = `Samples: ${passed}/${total} Passed`;
        gradeBadge.className = `score-banner ${passed === total ? 'score-pass' : 'score-fail'}`;
      }
      document.getElementById('exec-status').textContent = data.exit_code === 0 ? 'Samples Passed' : 'Samples Failed';
    }

    async function onEvaluate() {
      document.getElementById('exec-status').textContent = 'Evaluating...';
      const terminal = document.getElementById('terminal');
      terminal.textContent = 'Running complete VPL test suite against student_code.py...\\n';
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exam: currentExam, q: currentQ, code: editor.getValue() })
      });
      const data = await res.json();
      terminal.textContent = data.output;

      // Parse score from output
      const gradeMatch = data.output.match(/Grade :=>> (\\d+)/);
      const gradeBadge = document.getElementById('grade-badge');
      if (gradeMatch) {
        const score = parseInt(gradeMatch[1]);
        const maxScore = problemData.marks || 40;
        gradeBadge.className = 'score-banner ' + (score === maxScore ? 'score-pass' : 'score-fail');
        gradeBadge.textContent = `GRADE: ${score} / ${maxScore}`;
      } else {
        gradeBadge.textContent = '';
      }

      document.getElementById('exec-status').textContent = data.exit_code === 0 ? 'Evaluation Complete' : 'Tests Failed';
    }

    function switchQuestion(q) {
      currentQ = q;
      document.getElementById('q1-btn').classList.toggle('active', q === 'q1');
      document.getElementById('q2-btn').classList.toggle('active', q === 'q2');
      loadProblem();
    }

    function onExamChange() {
      currentExam = document.getElementById('exam-select').value;
      loadProblem();
    }

    function switchFileTab(tab) {
      currentFileTab = tab;
      document.getElementById('tab-student').classList.toggle('active', tab === 'student');
      document.getElementById('tab-common').classList.toggle('active', tab === 'common');
      document.getElementById('tab-readme').classList.toggle('active', tab === 'readme');
      renderEditorContent();
    }

    function toggleTimer() {
      timerRunning = !timerRunning;
      const t = document.getElementById('timer');
      if (timerRunning) {
        t.classList.remove('paused');
        timerInterval = setInterval(() => {
          if (timeLeft > 0) {
            timeLeft--;
            const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
            const s = String(timeLeft % 60).padStart(2, '0');
            t.textContent = `${m}:${s} [Space]`;
          }
        }, 1000);
      } else {
        t.classList.add('paused');
        clearInterval(timerInterval);
      }
    }

    // Global keyboard shortcuts (Timer pause/resume and Font Zoom)
    window.addEventListener('keydown', (e) => {
      // Ctrl+= / Cmd+=, Ctrl+- / Cmd+-, Ctrl+0 / Cmd+0
      if ((e.ctrlKey || e.metaKey) && (e.key === '=' || e.key === '+' || e.key === '-' || e.key === '0')) {
        if (e.key === '=' || e.key === '+') {
          e.preventDefault();
          stepFontSize(1);
          return;
        } else if (e.key === '-') {
          e.preventDefault();
          stepFontSize(-1);
          return;
        } else if (e.key === '0') {
          e.preventDefault();
          applyFontSize(13);
          return;
        }
      }

      if ((e.code === 'Space' || e.key === 'p' || e.key === 'P') && !editor.isFocused()) {
        const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
        if (tag === 'select' || tag === 'input' || tag === 'button') return;
        e.preventDefault();
        toggleTimer();
      }
    });

    window.onload = () => {
      initPortalTheme();
      initAce();
      loadProblem();
    };
  </script>
</body>
</html>"""
        self.wfile.write(html_content.encode("utf-8"))


def main():
    port = 8080
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, VPLHandler)
    print(f"============================================================")
    print(f"  IIT Delhi VPL Local Exam Server Running on http://127.0.0.1:{port}")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
