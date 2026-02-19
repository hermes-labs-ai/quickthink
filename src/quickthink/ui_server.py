from __future__ import annotations

"""
Local-only evaluation UI server.

Purpose:
- Fast browser workflow for running QuickThink prompts/evals without CLI.
- Mirrors runtime controls (`lite` / `two_pass`, routing visibility, latency metrics).

Status:
- Internal integration sandbox for team testing.
- Not part of the core publishable runtime path unless explicitly promoted.

Agent guidance:
- Keep core engine logic in `engine.py`; this file should stay a thin UI adapter.
- Prefer adding eval/review UX here over changing core behavior.
"""

import json
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .config import MODEL_PROFILES, QuickThinkConfig
from .engine import QuickThinkEngine

HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>quickthink eval UI</title>
  <style>
    :root {
      --bg: #f6efe5;
      --ink: #111111;
      --panel: #fffaf3;
      --accent: #d9480f;
      --accent-2: #0b6e4f;
      --muted: #5f5f5f;
      --ring: #131313;
      --border: #d7c9b6;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Space Grotesk", "Avenir Next", "Helvetica Neue", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at 10% -10%, #f3ccb1 0%, transparent 60%),
        radial-gradient(800px 450px at 100% 0%, #cce6dd 0%, transparent 55%),
        var(--bg);
      min-height: 100vh;
      padding: 1.25rem;
      animation: fadeIn .3s ease-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
      display: grid;
      gap: 1rem;
      grid-template-columns: 1fr;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.04);
    }
    h1 {
      margin: 0;
      letter-spacing: .4px;
      font-size: 1.5rem;
    }
    p { margin: .4rem 0 0 0; color: var(--muted); }
    .grid {
      display: grid;
      gap: .8rem;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .full { grid-column: 1 / -1; }
    label {
      font-size: .86rem;
      font-weight: 600;
      margin-bottom: .3rem;
      display: block;
    }
    input, select, textarea, button {
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #fffcf8;
      color: var(--ink);
      padding: .65rem .75rem;
      font-size: .95rem;
      font-family: inherit;
    }
    textarea {
      resize: vertical;
      min-height: 120px;
      line-height: 1.35;
    }
    input:focus, select:focus, textarea:focus {
      outline: 2px solid var(--ring);
      outline-offset: 1px;
    }
    .checks {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: .3rem;
    }
    .checks label {
      display: flex;
      align-items: center;
      gap: .4rem;
      margin: 0;
      font-weight: 500;
    }
    .checks input {
      width: auto;
    }
    .actions {
      display: flex;
      gap: .6rem;
      justify-content: flex-end;
      margin-top: .6rem;
    }
    button {
      width: auto;
      cursor: pointer;
      font-weight: 700;
      border-color: #111111;
      background: #ffffff;
    }
    .primary {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }
    .secondary {
      background: var(--accent-2);
      color: #fff;
      border-color: var(--accent-2);
    }
    .status {
      font-size: .9rem;
      margin-top: .5rem;
      color: var(--muted);
      min-height: 1.4rem;
    }
    .result {
      white-space: pre-wrap;
      line-height: 1.45;
      padding: .8rem;
      border-radius: 10px;
      border: 1px dashed var(--border);
      background: #fff;
      min-height: 80px;
      margin-top: .4rem;
    }
    .metrics {
      display: grid;
      gap: .6rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .metric {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: .6rem;
      background: #fff;
    }
    .metric .k { color: var(--muted); font-size: .8rem; }
    .metric .v { font-weight: 700; margin-top: .2rem; }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      .metrics { grid-template-columns: 1fr; }
      .actions { justify-content: stretch; }
      button { flex: 1; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="panel">
      <h1>quickthink eval UI</h1>
      <p>Run prompts against local Ollama with the same scaffolding settings as your CLI.</p>
    </section>

    <section class="panel">
      <h1>Preflight</h1>
      <p>Required before eval runs. Uses validate_prompt_set.py.</p>
      <div class="grid">
        <div class="full">
          <label for="promptSetPath">Prompt set path</label>
          <input id="promptSetPath" value="docs/evals/prompt_set.jsonl" />
        </div>
      </div>
      <div class="actions">
        <button id="preflightBtn" class="secondary">Run preflight</button>
      </div>
      <div id="preflightStatus" class="status"></div>
      <div class="result" id="preflightSha">Dataset SHA256: (not validated)</div>
      <div class="result" id="preflightOutput"></div>
    </section>

    <section class="panel">
      <div class="grid">
        <div>
          <label for="model">Model</label>
          <select id="model"></select>
        </div>
        <div>
          <label for="mode">Mode</label>
          <select id="mode">
            <option value="direct">direct (raw)</option>
            <option value="lite">lite</option>
            <option value="two_pass">two_pass</option>
          </select>
        </div>
        <div class="full">
          <label for="ollamaUrl">Ollama URL</label>
          <input id="ollamaUrl" value="http://localhost:11434" />
        </div>
        <div class="full">
          <label for="prompt">Prompt</label>
          <textarea id="prompt" placeholder="Enter prompt for your eval case..."></textarea>
        </div>
        <div class="full">
          <label for="continuity">Continuity hint (optional)</label>
          <input id="continuity" placeholder="ctx:prior_goal,format_json" />
        </div>
        <div class="full">
          <div class="checks">
            <label><input id="bypass" type="checkbox" checked /> bypass short prompts</label>
            <label><input id="showPlan" type="checkbox" checked /> show plan</label>
            <label><input id="showRoute" type="checkbox" checked /> show route info</label>
          </div>
        </div>
      </div>
      <div class="actions">
        <button id="clearBtn">Clear</button>
        <button id="runAllBtn" class="secondary">Run 3 modes (typed prompt)</button>
        <button id="runBtn" class="primary">Run prompt</button>
      </div>
      <div id="status" class="status"></div>
    </section>

    <section class="panel">
      <h1>Run File Ingestion</h1>
      <p>Ingestion is blocked unless validate_results.py returns status=OK.</p>
      <div class="grid">
        <div class="full">
          <label for="runFilePath">Run file path (JSONL)</label>
          <input id="runFilePath" placeholder="docs/evals/results/run-YYYYMMDD-HHMM-batch.jsonl" />
        </div>
        <div>
          <label for="expectedPrompts">Expected prompts</label>
          <input id="expectedPrompts" type="number" value="120" min="0" />
        </div>
        <div>
          <label for="expectedRuns">Expected runs</label>
          <input id="expectedRuns" type="number" value="3" min="0" />
        </div>
        <div class="full">
          <label for="models">Models (space-separated)</label>
          <input id="models" value="qwen2.5:1.5b mistral:7b gemma3:27b" />
        </div>
      </div>
      <div class="actions">
        <button id="ingestBtn" class="secondary">Validate + ingest run file</button>
      </div>
      <div id="ingestStatus" class="status"></div>
      <div class="result" id="ingestOutput"></div>
    </section>

    <section class="panel">
      <h1>Eval Set Runner</h1>
      <p>Run prompt_set.jsonl across direct/lite/two_pass with run manifest output.</p>
      <div class="grid">
        <div class="full">
          <label for="evalPromptSetPath">Prompt set path</label>
          <input id="evalPromptSetPath" value="docs/evals/prompt_set.jsonl" />
        </div>
        <div class="full">
          <label for="evalOutPath">Results JSONL out</label>
          <input id="evalOutPath" value="docs/evals/results/run_results.jsonl" />
        </div>
        <div class="full">
          <label for="evalManifestPath">Manifest out</label>
          <input id="evalManifestPath" value="docs/evals/results/run_manifest.json" />
        </div>
        <div>
          <label for="evalRuns">Runs per prompt</label>
          <input id="evalRuns" type="number" value="3" min="1" />
        </div>
        <div>
          <label for="evalLimit">Prompt limit (0=all)</label>
          <input id="evalLimit" type="number" value="0" min="0" />
        </div>
        <div class="full">
          <label for="evalModels">Models (space-separated)</label>
          <input id="evalModels" value="qwen2.5:1.5b mistral:7b gemma3:27b" />
        </div>
      </div>
      <div class="actions">
        <button id="runEvalSetBtn" class="secondary">Run eval set</button>
      </div>
      <div id="evalSetStatus" class="status"></div>
      <div class="result" id="evalSetOutput"></div>
    </section>

    <section class="panel">
      <h1>Prompt Set Browser</h1>
      <div class="grid">
        <div class="full">
          <label for="browsePromptPath">Prompt set JSONL path</label>
          <input id="browsePromptPath" value="docs/evals/prompt_set.jsonl" />
        </div>
      </div>
      <div class="actions">
        <button id="loadPromptsBtn">Load prompts</button>
      </div>
      <div id="promptBrowseStatus" class="status"></div>
      <div class="result" id="promptBrowseOutput"></div>
    </section>

    <section class="panel">
      <h1>Results Browser</h1>
      <div class="grid">
        <div class="full">
          <label for="resultsFileSelect">Result file</label>
          <select id="resultsFileSelect"></select>
        </div>
      </div>
      <div class="actions">
        <button id="refreshResultFilesBtn">Refresh files</button>
        <button id="loadResultRowsBtn">Load rows</button>
      </div>
      <div id="resultsBrowseStatus" class="status"></div>
      <div class="result" id="resultsBrowseOutput"></div>
    </section>

    <section class="panel">
      <h1>Results</h1>
      <div id="metrics" class="metrics"></div>
      <div class="result" id="answer"></div>
      <div class="result" id="plan"></div>
      <div class="result" id="route"></div>
      <div class="result" id="allModes"></div>
    </section>
  </div>

  <script>
    const modelEl = document.getElementById("model");
    const modeEl = document.getElementById("mode");
    const promptEl = document.getElementById("prompt");
    const ollamaEl = document.getElementById("ollamaUrl");
    const continuityEl = document.getElementById("continuity");
    const bypassEl = document.getElementById("bypass");
    const showPlanEl = document.getElementById("showPlan");
    const showRouteEl = document.getElementById("showRoute");
    const statusEl = document.getElementById("status");
    const answerEl = document.getElementById("answer");
    const planEl = document.getElementById("plan");
    const routeEl = document.getElementById("route");
    const allModesEl = document.getElementById("allModes");
    const metricsEl = document.getElementById("metrics");
    const runBtn = document.getElementById("runBtn");
    const runAllBtn = document.getElementById("runAllBtn");
    const clearBtn = document.getElementById("clearBtn");
    const preflightBtn = document.getElementById("preflightBtn");
    const preflightStatusEl = document.getElementById("preflightStatus");
    const preflightShaEl = document.getElementById("preflightSha");
    const preflightOutputEl = document.getElementById("preflightOutput");
    const promptSetPathEl = document.getElementById("promptSetPath");
    const ingestBtn = document.getElementById("ingestBtn");
    const runFilePathEl = document.getElementById("runFilePath");
    const expectedPromptsEl = document.getElementById("expectedPrompts");
    const expectedRunsEl = document.getElementById("expectedRuns");
    const modelsEl = document.getElementById("models");
    const ingestStatusEl = document.getElementById("ingestStatus");
    const ingestOutputEl = document.getElementById("ingestOutput");
    const evalPromptSetPathEl = document.getElementById("evalPromptSetPath");
    const evalOutPathEl = document.getElementById("evalOutPath");
    const evalManifestPathEl = document.getElementById("evalManifestPath");
    const evalRunsEl = document.getElementById("evalRuns");
    const evalLimitEl = document.getElementById("evalLimit");
    const evalModelsEl = document.getElementById("evalModels");
    const runEvalSetBtn = document.getElementById("runEvalSetBtn");
    const evalSetStatusEl = document.getElementById("evalSetStatus");
    const evalSetOutputEl = document.getElementById("evalSetOutput");
    const browsePromptPathEl = document.getElementById("browsePromptPath");
    const loadPromptsBtn = document.getElementById("loadPromptsBtn");
    const promptBrowseStatusEl = document.getElementById("promptBrowseStatus");
    const promptBrowseOutputEl = document.getElementById("promptBrowseOutput");
    const resultsFileSelectEl = document.getElementById("resultsFileSelect");
    const refreshResultFilesBtn = document.getElementById("refreshResultFilesBtn");
    const loadResultRowsBtn = document.getElementById("loadResultRowsBtn");
    const resultsBrowseStatusEl = document.getElementById("resultsBrowseStatus");
    const resultsBrowseOutputEl = document.getElementById("resultsBrowseOutput");

    function setStatus(text) {
      statusEl.textContent = text;
    }

    function fmtMs(v) {
      return Number(v || 0).toFixed(2) + " ms";
    }

    function setPreflightState(ok, sha) {
      runBtn.disabled = !ok;
      preflightStatusEl.textContent = ok
        ? "Preflight OK. Eval runs are enabled."
        : "Preflight required. Eval runs are blocked.";
      preflightShaEl.textContent = "Dataset SHA256: " + (sha || "(not available)");
    }

    function renderMetrics(data) {
      const items = [
        ["Plan latency", fmtMs(data.plan_latency_ms)],
        ["Answer latency", fmtMs(data.answer_latency_ms)],
        ["Total latency", fmtMs(data.total_latency_ms)],
        ["Mode", data.mode],
        ["Bypassed", String(data.bypassed)],
        ["Plan repaired", String(data.plan_repaired)],
      ];
      metricsEl.innerHTML = "";
      for (const [k, v] of items) {
        const card = document.createElement("div");
        card.className = "metric";
        card.innerHTML = '<div class="k">' + k + '</div><div class="v">' + v + "</div>";
        metricsEl.appendChild(card);
      }
    }

    async function loadModels() {
      const res = await fetch("/api/models");
      const data = await res.json();
      modelEl.innerHTML = "";
      for (const m of data.models) {
        const o = document.createElement("option");
        o.value = m;
        o.textContent = m;
        modelEl.appendChild(o);
      }
    }

    async function refreshGateState() {
      const res = await fetch("/api/state");
      const data = await res.json();
      setPreflightState(Boolean(data.preflight_ok), data.dataset_sha256 || "");
      if (data.preflight_output) {
        preflightOutputEl.textContent = data.preflight_output;
      }
      if (data.last_ingestion && data.last_ingestion.output) {
        ingestOutputEl.textContent = data.last_ingestion.output;
      }
    }

    async function runPreflight() {
      preflightBtn.disabled = true;
      preflightStatusEl.textContent = "Running preflight...";
      try {
        const res = await fetch("/api/preflight", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path: promptSetPathEl.value.trim() || "docs/evals/prompt_set.jsonl" })
        });
        const data = await res.json();
        preflightOutputEl.textContent = data.output || "";
        setPreflightState(Boolean(data.preflight_ok), data.dataset_sha256 || "");
        if (!res.ok) {
          preflightStatusEl.textContent = "Preflight failed.";
          return;
        }
        preflightStatusEl.textContent = "Preflight complete.";
      } catch (err) {
        preflightStatusEl.textContent = "Preflight error: " + err.message;
      } finally {
        preflightBtn.disabled = false;
      }
    }

    async function validateAndIngestRunFile() {
      const path = runFilePathEl.value.trim();
      if (!path) {
        ingestStatusEl.textContent = "Run file path is required.";
        return;
      }
      ingestBtn.disabled = true;
      ingestStatusEl.textContent = "Validating run file...";
      try {
        const res = await fetch("/api/ingest-run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            path,
            expected_prompts: Number(expectedPromptsEl.value || "0"),
            expected_runs: Number(expectedRunsEl.value || "0"),
            models: (modelsEl.value || "").trim().split(/\s+/).filter(Boolean)
          })
        });
        const data = await res.json();
        ingestOutputEl.textContent = data.output || "";
        ingestStatusEl.textContent = data.ingested
          ? "Ingested. Validation status=OK."
          : "Blocked. Validation did not return status=OK.";
      } catch (err) {
        ingestStatusEl.textContent = "Ingestion error: " + err.message;
      } finally {
        ingestBtn.disabled = false;
      }
    }

    async function runEvalSet() {
      runEvalSetBtn.disabled = true;
      evalSetStatusEl.textContent = "Running eval set...";
      evalSetOutputEl.textContent = "";
      try {
        const res = await fetch("/api/run-eval-set", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt_set: evalPromptSetPathEl.value.trim() || "docs/evals/prompt_set.jsonl",
            out: evalOutPathEl.value.trim() || "docs/evals/results/run_results.jsonl",
            manifest_out: evalManifestPathEl.value.trim() || "docs/evals/results/run_manifest.json",
            runs: Number(evalRunsEl.value || "3"),
            limit: Number(evalLimitEl.value || "0"),
            models: (evalModelsEl.value || "").trim().split(/\s+/).filter(Boolean),
            ollama_url: ollamaEl.value.trim() || "http://localhost:11434",
            continuity_hint: continuityEl.value.trim() || null
          })
        });
        const data = await res.json();
        evalSetOutputEl.textContent = data.output || "";
        if (!res.ok) {
          throw new Error(data.error || "Eval set run failed");
        }
        evalSetStatusEl.textContent = "Eval set run complete.";
        runFilePathEl.value = data.out_path || runFilePathEl.value;
      } catch (err) {
        evalSetStatusEl.textContent = "Eval set error: " + err.message;
      } finally {
        runEvalSetBtn.disabled = false;
      }
    }

    function toPrettyJsonLines(rows, maxRows) {
      const slice = rows.slice(0, maxRows);
      return slice.map((row) => JSON.stringify(row, null, 2)).join("\\n\\n");
    }

    async function loadPromptRows() {
      const path = browsePromptPathEl.value.trim() || "docs/evals/prompt_set.jsonl";
      loadPromptsBtn.disabled = true;
      promptBrowseStatusEl.textContent = "Loading prompts...";
      try {
        const res = await fetch("/api/prompts?path=" + encodeURIComponent(path) + "&offset=0&limit=20");
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "failed loading prompts");
        }
        promptBrowseStatusEl.textContent = "Loaded " + data.rows.length + " of " + data.total + " prompt rows.";
        promptBrowseOutputEl.textContent = toPrettyJsonLines(data.rows, 20);
      } catch (err) {
        promptBrowseStatusEl.textContent = "Prompt load error: " + err.message;
      } finally {
        loadPromptsBtn.disabled = false;
      }
    }

    async function refreshResultFiles() {
      refreshResultFilesBtn.disabled = true;
      resultsBrowseStatusEl.textContent = "Refreshing result files...";
      try {
        const res = await fetch("/api/results/files");
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "failed listing result files");
        }
        resultsFileSelectEl.innerHTML = "";
        for (const file of data.files) {
          const opt = document.createElement("option");
          opt.value = file.path;
          opt.textContent = file.path + " (" + file.size_bytes + " bytes)";
          resultsFileSelectEl.appendChild(opt);
        }
        resultsBrowseStatusEl.textContent = "Found " + data.files.length + " result files.";
        if (data.files.length === 0) {
          resultsBrowseOutputEl.textContent = "(no .jsonl files under docs/evals/results)";
        }
      } catch (err) {
        resultsBrowseStatusEl.textContent = "Result file list error: " + err.message;
      } finally {
        refreshResultFilesBtn.disabled = false;
      }
    }

    async function loadResultRows() {
      const path = (resultsFileSelectEl.value || "").trim();
      if (!path) {
        resultsBrowseStatusEl.textContent = "Select a result file first.";
        return;
      }
      loadResultRowsBtn.disabled = true;
      resultsBrowseStatusEl.textContent = "Loading result rows...";
      try {
        const res = await fetch("/api/results/rows?path=" + encodeURIComponent(path) + "&offset=0&limit=20");
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "failed loading result rows");
        }
        resultsBrowseStatusEl.textContent = "Loaded " + data.rows.length + " of " + data.total + " rows from " + data.path;
        resultsBrowseOutputEl.textContent = toPrettyJsonLines(data.rows, 20);
      } catch (err) {
        resultsBrowseStatusEl.textContent = "Result rows error: " + err.message;
      } finally {
        loadResultRowsBtn.disabled = false;
      }
    }

    function renderAllModes(results) {
      const order = ["direct", "lite", "two_pass"];
      const sections = [];
      for (const mode of order) {
        const data = results[mode];
        if (!data) {
          continue;
        }
        sections.push(
          [
            mode === "direct" ? "Mode: direct (raw)" : "Mode: " + mode,
            "total_latency_ms=" + Number(data.total_latency_ms || 0).toFixed(2),
            "plan_latency_ms=" + Number(data.plan_latency_ms || 0).toFixed(2),
            "answer_latency_ms=" + Number(data.answer_latency_ms || 0).toFixed(2),
            "bypassed=" + String(data.bypassed),
            "route_score=" + String(data.route_score),
            "selected_plan_budget=" + String(data.selected_plan_budget),
            "",
            "Plan:",
            data.plan || "(none)",
            "",
            "Answer:",
            data.answer || "(empty)",
          ].join("\\n")
        );
      }
      allModesEl.textContent = sections.join("\\n\\n----------------------------------------\\n\\n");
    }

    async function runAllModes() {
      const prompt = promptEl.value.trim();
      if (!prompt) {
        setStatus("No typed prompt found. Running eval-set flow instead...");
        await runEvalSet();
        return;
      }
      runAllBtn.disabled = true;
      runBtn.disabled = true;
      setStatus("Running all three modes...");
      answerEl.textContent = "";
      planEl.textContent = "";
      routeEl.textContent = "";
      allModesEl.textContent = "";
      metricsEl.innerHTML = "";
      try {
        const res = await fetch("/api/ask-all", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt,
            model: modelEl.value,
            ollama_url: ollamaEl.value.trim(),
            bypass_short_prompts: bypassEl.checked,
            continuity_hint: continuityEl.value.trim() || null
          })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Request failed");
        }
        renderAllModes(data.results || {});
        if (data.results && data.results.lite) {
          renderMetrics(data.results.lite);
        }
        setStatus("Complete (direct + lite + two_pass).");
      } catch (err) {
        setStatus("Error: " + err.message);
      } finally {
        runAllBtn.disabled = false;
        runBtn.disabled = false;
      }
    }

    async function runPrompt() {
      const prompt = promptEl.value.trim();
      if (!prompt) {
        setStatus("Prompt is required.");
        return;
      }
      runBtn.disabled = true;
      runAllBtn.disabled = true;
      setStatus("Running...");
      answerEl.textContent = "";
      planEl.textContent = "";
      routeEl.textContent = "";
      allModesEl.textContent = "";
      metricsEl.innerHTML = "";

      try {
        const res = await fetch("/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt,
            model: modelEl.value,
            mode: modeEl.value,
            ollama_url: ollamaEl.value.trim(),
            bypass_short_prompts: bypassEl.checked,
            continuity_hint: continuityEl.value.trim() || null
          })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Request failed");
        }
        answerEl.textContent = "Answer\\n\\n" + (data.answer || "(empty)");
        planEl.textContent = showPlanEl.checked
          ? "Plan\\n\\n" + (data.plan || "(none)")
          : "Plan hidden";
        routeEl.textContent = showRouteEl.checked
          ? "Route\\n\\n" + [
              "mode=" + data.mode,
              "bypassed=" + data.bypassed,
              "score=" + data.route_score,
              "plan_budget=" + data.selected_plan_budget
            ].join(" ")
          : "Route info hidden";
        renderMetrics(data);
        setStatus("Complete.");
      } catch (err) {
        setStatus("Error: " + err.message);
      } finally {
        runBtn.disabled = false;
        runAllBtn.disabled = false;
      }
    }

    function clearResults() {
      answerEl.textContent = "";
      planEl.textContent = "";
      routeEl.textContent = "";
      allModesEl.textContent = "";
      metricsEl.innerHTML = "";
      setStatus("");
    }

    runBtn.addEventListener("click", runPrompt);
    runAllBtn.addEventListener("click", runAllModes);
    clearBtn.addEventListener("click", clearResults);
    preflightBtn.addEventListener("click", runPreflight);
    ingestBtn.addEventListener("click", validateAndIngestRunFile);
    runEvalSetBtn.addEventListener("click", runEvalSet);
    loadPromptsBtn.addEventListener("click", loadPromptRows);
    refreshResultFilesBtn.addEventListener("click", refreshResultFiles);
    loadResultRowsBtn.addEventListener("click", loadResultRows);
    loadModels().catch((err) => setStatus("Failed loading models: " + err.message));
    refreshGateState().catch((err) => preflightStatusEl.textContent = "State load failed: " + err.message);
    refreshResultFiles().catch((err) => resultsBrowseStatusEl.textContent = "Result file list error: " + err.message);
    loadPromptRows().catch((err) => promptBrowseStatusEl.textContent = "Prompt load error: " + err.message);
  </script>
</body>
</html>
"""

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_VALIDATOR = REPO_ROOT / "scripts" / "evals" / "validate_prompt_set.py"
RESULTS_VALIDATOR = REPO_ROOT / "scripts" / "evals" / "validate_results.py"
RUN_SUITE_SCRIPT = REPO_ROOT / "scripts" / "eval_harness" / "run_suite.py"
PROMPT_SET_DEFAULT = REPO_ROOT / "docs" / "evals" / "prompt_set.jsonl"
RESULTS_DIR_DEFAULT = REPO_ROOT / "docs" / "evals" / "results"
PROMPTS_DIR_DEFAULT = REPO_ROOT / "docs" / "evals"


def _extract_key(output: str, key: str) -> str | None:
    prefix = f"{key}="
    for line in output.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _validator_status(output: str, returncode: int) -> str:
    status = _extract_key(output, "status")
    if status:
        return status
    return "OK" if returncode == 0 else "FAILED"


def _run_validator(cmd: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = proc.stdout
    if proc.stderr.strip():
        output = f"{output}\n{proc.stderr}" if output else proc.stderr
    status = _validator_status(output, proc.returncode)
    return {
        "status": status,
        "ok": status == "OK",
        "output": output.strip(),
        "returncode": proc.returncode,
        "sha256": _extract_key(output, "sha256"),
    }


def _count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                count += 1
    return count


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_repo_path(path_raw: str, *, allowed_root: Path | None = None) -> Path:
    raw = path_raw.strip()
    if not raw:
        raise ValueError("path cannot be empty")

    candidate = Path(raw)
    resolved = candidate.resolve() if candidate.is_absolute() else (REPO_ROOT / candidate).resolve()

    if not _is_relative_to(resolved, REPO_ROOT.resolve()):
        raise ValueError("path must stay within repository root")
    if allowed_root is not None and not _is_relative_to(resolved, allowed_root.resolve()):
        rel = allowed_root.relative_to(REPO_ROOT)
        raise ValueError(f"path must stay within {rel}")
    return resolved


def _read_jsonl_page(path: Path, offset: int, limit: int) -> dict[str, object]:
    if offset < 0:
        offset = 0
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    rows: list[dict[str, object]] = []
    total = 0
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            if total >= offset and len(rows) < limit:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {lineno}: top-level value must be an object")
                rows.append(value)
            total += 1
    return {"rows": rows, "total": total, "offset": offset, "limit": limit}


def _list_result_jsonl_files() -> list[dict[str, object]]:
    if not RESULTS_DIR_DEFAULT.exists():
        return []
    files: list[dict[str, object]] = []
    for path in sorted(RESULTS_DIR_DEFAULT.glob("*.jsonl")):
        stat = path.stat()
        files.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "size_bytes": int(stat.st_size),
                "modified_epoch": float(stat.st_mtime),
            }
        )
    files.sort(key=lambda x: x["modified_epoch"], reverse=True)
    return files


def _result_payload(result: object) -> dict[str, object]:
    return {
        "answer": result.answer,
        "plan": result.plan,
        "mode": result.mode,
        "bypassed": result.bypassed,
        "route_score": result.route_score,
        "selected_plan_budget": result.selected_plan_budget,
        "plan_repaired": result.plan_repaired,
        "plan_latency_ms": round(result.plan_latency_ms, 2),
        "answer_latency_ms": round(result.answer_latency_ms, 2),
        "total_latency_ms": round(result.total_latency_ms, 2),
    }


def _run_eval_mode(
    *,
    prompt: str,
    model: str,
    mode: str,
    ollama_url: str,
    bypass_short_prompts: bool,
    continuity_hint: object,
) -> dict[str, object]:
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config.continuity_hint = str(continuity_hint).strip() if continuity_hint else None

    if mode == "direct":
        config.mode = "direct"
        config.adaptive_routing = False
        config.bypass_short_prompts = True
        config.bypass_char_threshold = 10_000_000
    else:
        config.mode = mode
        config.bypass_short_prompts = bypass_short_prompts

    result = QuickThinkEngine(config).run(prompt)
    return _result_payload(result)


def serve_ui(host: str = "127.0.0.1", port: int = 7860, open_browser: bool = False) -> None:
    state_lock = threading.Lock()
    state: dict[str, object] = {
        "preflight_ok": False,
        "dataset_sha256": None,
        "preflight_output": "",
        "last_ingestion": None,
    }

    class Handler(BaseHTTPRequestHandler):
        def _json(self, code: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _html(self, body: str) -> None:
            raw = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlsplit(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)

            if path == "/":
                self._html(HTML_PAGE)
                return
            if path == "/api/models":
                self._json(200, {"models": list(MODEL_PROFILES.keys())})
                return
            if path == "/api/state":
                with state_lock:
                    payload = dict(state)
                self._json(200, payload)
                return
            if path == "/api/prompts":
                prompt_set = str(query.get("path", [str(PROMPT_SET_DEFAULT.relative_to(REPO_ROOT))])[0])
                offset = int(query.get("offset", ["0"])[0])
                limit = int(query.get("limit", ["20"])[0])
                try:
                    resolved = _resolve_repo_path(prompt_set, allowed_root=PROMPTS_DIR_DEFAULT)
                    if not resolved.exists():
                        self._json(404, {"error": f"file not found: {prompt_set}"})
                        return
                    page = _read_jsonl_page(resolved, offset=offset, limit=limit)
                except Exception as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(
                    200,
                    {
                        "path": prompt_set,
                        "rows": page["rows"],
                        "total": page["total"],
                        "offset": page["offset"],
                        "limit": page["limit"],
                    },
                )
                return
            if path == "/api/results/files":
                self._json(200, {"files": _list_result_jsonl_files()})
                return
            if path == "/api/results/rows":
                result_path = str(query.get("path", [""])[0]).strip()
                if not result_path:
                    self._json(400, {"error": "path query parameter is required"})
                    return
                offset = int(query.get("offset", ["0"])[0])
                limit = int(query.get("limit", ["20"])[0])
                try:
                    resolved = _resolve_repo_path(result_path, allowed_root=RESULTS_DIR_DEFAULT)
                    if not resolved.exists():
                        self._json(404, {"error": f"file not found: {result_path}"})
                        return
                    page = _read_jsonl_page(resolved, offset=offset, limit=limit)
                except Exception as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(
                    200,
                    {
                        "path": result_path,
                        "rows": page["rows"],
                        "total": page["total"],
                        "offset": page["offset"],
                        "limit": page["limit"],
                    },
                )
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            try:
                raw_len = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(raw_len)
                payload = json.loads(raw.decode("utf-8"))

                if self.path == "/api/preflight":
                    prompt_set_path = str(payload.get("path", "docs/evals/prompt_set.jsonl")).strip()
                    try:
                        resolved_prompt_set = _resolve_repo_path(
                            prompt_set_path,
                            allowed_root=PROMPTS_DIR_DEFAULT,
                        )
                    except Exception as exc:
                        self._json(400, {"error": str(exc), "preflight_ok": False})
                        return
                    cmd = [sys.executable, str(PROMPT_VALIDATOR), "--path", str(resolved_prompt_set)]
                    result = _run_validator(cmd)
                    with state_lock:
                        state["preflight_ok"] = result["ok"]
                        state["dataset_sha256"] = result["sha256"]
                        state["preflight_output"] = result["output"]
                    code = 200 if result["ok"] else 400
                    self._json(
                        code,
                        {
                            "preflight_ok": result["ok"],
                            "status": result["status"],
                            "dataset_sha256": result["sha256"],
                            "output": result["output"],
                        },
                    )
                    return

                if self.path == "/api/ingest-run":
                    run_path_raw = str(payload.get("path", "")).strip()
                    if not run_path_raw:
                        self._json(400, {"error": "path is required", "ingested": False})
                        return
                    try:
                        resolved_run_path = _resolve_repo_path(run_path_raw, allowed_root=RESULTS_DIR_DEFAULT)
                    except Exception as exc:
                        self._json(400, {"error": str(exc), "ingested": False})
                        return
                    expected_prompts = int(payload.get("expected_prompts", 0) or 0)
                    expected_runs = int(payload.get("expected_runs", 0) or 0)
                    models = payload.get("models", [])
                    if isinstance(models, str):
                        models_list = [m for m in models.split() if m]
                    else:
                        models_list = [str(m).strip() for m in models if str(m).strip()]

                    cmd = [
                        sys.executable,
                        str(RESULTS_VALIDATOR),
                        "--path",
                        str(resolved_run_path),
                        "--expected-prompts",
                        str(expected_prompts),
                        "--expected-runs",
                        str(expected_runs),
                    ]
                    if models_list:
                        cmd.extend(["--models", *models_list])
                    result = _run_validator(cmd)

                    if not result["ok"]:
                        with state_lock:
                            state["last_ingestion"] = {
                                "ingested": False,
                                "path": run_path_raw,
                                "output": result["output"],
                                "status": result["status"],
                            }
                        self._json(
                            400,
                            {
                                "ingested": False,
                                "status": result["status"],
                                "output": result["output"],
                            },
                        )
                        return

                    rows = _count_jsonl_rows(resolved_run_path)
                    ingestion_payload = {
                        "ingested": True,
                        "path": str(resolved_run_path.relative_to(REPO_ROOT)),
                        "rows": rows,
                        "status": result["status"],
                        "output": result["output"],
                    }
                    with state_lock:
                        state["last_ingestion"] = ingestion_payload
                    self._json(200, ingestion_payload)
                    return

                if self.path == "/api/run-eval-set":
                    with state_lock:
                        preflight_ok = bool(state.get("preflight_ok"))
                        dataset_sha256 = state.get("dataset_sha256")
                    if not preflight_ok:
                        self._json(
                            409,
                            {
                                "error": "Preflight required: run validate_prompt_set.py and obtain status=OK before eval runs.",
                                "dataset_sha256": dataset_sha256,
                            },
                        )
                        return

                    prompt_set = str(payload.get("prompt_set", "docs/evals/prompt_set.jsonl")).strip()
                    out_path = str(payload.get("out", "docs/evals/results/run_results.jsonl")).strip()
                    manifest_out = str(payload.get("manifest_out", "docs/evals/results/run_manifest.json")).strip()
                    runs = int(payload.get("runs", 3) or 3)
                    limit = int(payload.get("limit", 0) or 0)
                    ollama_url = str(payload.get("ollama_url", "http://localhost:11434")).strip()
                    continuity_hint = payload.get("continuity_hint", None)
                    models = payload.get("models", [])
                    if isinstance(models, str):
                        models_list = [m for m in models.split() if m]
                    else:
                        models_list = [str(m).strip() for m in models if str(m).strip()]
                    if runs < 1:
                        self._json(400, {"error": "runs must be >= 1"})
                        return
                    try:
                        resolved_prompt_set = _resolve_repo_path(prompt_set, allowed_root=PROMPTS_DIR_DEFAULT)
                        resolved_out_path = _resolve_repo_path(out_path, allowed_root=RESULTS_DIR_DEFAULT)
                        resolved_manifest_out = _resolve_repo_path(manifest_out, allowed_root=RESULTS_DIR_DEFAULT)
                    except Exception as exc:
                        self._json(400, {"error": str(exc)})
                        return

                    cmd = [
                        sys.executable,
                        str(RUN_SUITE_SCRIPT),
                        "--prompt-set",
                        str(resolved_prompt_set),
                        "--out",
                        str(resolved_out_path),
                        "--manifest-out",
                        str(resolved_manifest_out),
                        "--runs",
                        str(runs),
                        "--ollama-url",
                        ollama_url,
                    ]
                    if models_list:
                        cmd.extend(["--models", *models_list])
                    if limit > 0:
                        cmd.extend(["--limit", str(limit)])
                    if continuity_hint:
                        cmd.extend(["--continuity-hint", str(continuity_hint)])

                    proc = subprocess.run(
                        cmd,
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    output = (proc.stdout or "").strip()
                    if (proc.stderr or "").strip():
                        output = f"{output}\n{proc.stderr.strip()}" if output else proc.stderr.strip()
                    if proc.returncode != 0:
                        self._json(
                            400,
                            {
                                "error": "eval harness run failed",
                                "returncode": proc.returncode,
                                "output": output,
                            },
                        )
                        return
                    self._json(
                        200,
                        {
                            "status": "OK",
                            "out_path": str(resolved_out_path.relative_to(REPO_ROOT)),
                            "manifest_out": str(resolved_manifest_out.relative_to(REPO_ROOT)),
                            "output": output,
                        },
                    )
                    return

                if self.path not in {"/api/ask", "/api/ask-all"}:
                    self._json(404, {"error": "not found"})
                    return

                with state_lock:
                    preflight_ok = bool(state.get("preflight_ok"))
                    dataset_sha256 = state.get("dataset_sha256")
                if not preflight_ok:
                    self._json(
                        409,
                        {
                            "error": "Preflight required: run validate_prompt_set.py and obtain status=OK before eval runs.",
                            "dataset_sha256": dataset_sha256,
                        },
                    )
                    return

                prompt = str(payload.get("prompt", "")).strip()
                model = str(payload.get("model", "qwen2.5:1.5b")).strip()
                mode = str(payload.get("mode", "lite")).strip()
                ollama_url = str(payload.get("ollama_url", "http://localhost:11434")).strip()
                bypass_short_prompts = bool(payload.get("bypass_short_prompts", True))
                continuity_hint = payload.get("continuity_hint", None)

                if not prompt:
                    self._json(400, {"error": "prompt is required"})
                    return
                if mode not in {"direct", "lite", "two_pass"}:
                    self._json(400, {"error": "mode must be direct, lite, or two_pass"})
                    return
                if self.path == "/api/ask-all":
                    results = {
                        "direct": _run_eval_mode(
                            prompt=prompt,
                            model=model,
                            mode="direct",
                            ollama_url=ollama_url,
                            bypass_short_prompts=bypass_short_prompts,
                            continuity_hint=continuity_hint,
                        ),
                        "lite": _run_eval_mode(
                            prompt=prompt,
                            model=model,
                            mode="lite",
                            ollama_url=ollama_url,
                            bypass_short_prompts=bypass_short_prompts,
                            continuity_hint=continuity_hint,
                        ),
                        "two_pass": _run_eval_mode(
                            prompt=prompt,
                            model=model,
                            mode="two_pass",
                            ollama_url=ollama_url,
                            bypass_short_prompts=bypass_short_prompts,
                            continuity_hint=continuity_hint,
                        ),
                    }
                    self._json(200, {"results": results})
                    return

                payload_out = _run_eval_mode(
                    prompt=prompt,
                    model=model,
                    mode=mode,
                    ollama_url=ollama_url,
                    bypass_short_prompts=bypass_short_prompts,
                    continuity_hint=continuity_hint,
                )
                self._json(200, payload_out)
            except Exception as exc:  # pragma: no cover - network/runtime dependent
                self._json(500, {"error": str(exc)})

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    if open_browser:
        webbrowser.open(url)
    print(f"quickthink UI listening on {url}")
    server.serve_forever()
