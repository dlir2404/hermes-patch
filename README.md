# Hermes Agent Antigravity / 9Router Compatibility Patch 🚀

A lightweight, automated patch script for [Hermes Agent](https://github.com/NousResearch/hermes-agent) to work seamlessly with **9Router** and **Google Antigravity / Cloud Code PA** models (e.g. `ag/gemini-3.8-flash`, `gemini-2.5-pro`).

---

## 🛑 The Problem

When routing Hermes Agent queries through 9Router to Google Cloud Code PA (`cloudcode-pa.googleapis.com`), Google's upstream safety and provenance filter intercepts the request and throws a synthetic HTTP 429:

```text
HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute' of service 'cloudcode-pa.googleapis.com'...",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```

### Root Cause
This error is **not** a real quota exhaustion. Google Cloud Code PA actively filters system prompts containing verbatim phrases originating from Anthropic's Claude Code and OpenCode:
1. `DEFAULT_AGENT_IDENTITY`: Contains the verbatim Claude Code sizing & exploration rule.
2. `TASK_COMPLETION_GUIDANCE`: Verbatim Claude Code `"Finishing the job"` directive.
3. `GOOGLE_MODEL_OPERATIONAL_GUIDANCE`: Exact OpenCode header `"# Google model operational directives"`.
4. `SOUL.md`: Verbatim Nous/Claude persona.

---

## 🛠️ What This Patch Does

1. **Sanitizes Persona (`~/.hermes/SOUL.md`)**: Replaces trigger phrases with a clean, high-performance assistant directive.
2. **Patches Python Sources**: Modifies `prompt_builder.py` and `system_prompt.py` across:
   - Core repository: `~/.hermes/hermes-agent/`
   - All runtime environments: `~/.hermes/installs/*/environments/*/workspace/`
3. **Purges Bytecode**: Removes all compiled `*.pyc` and `__pycache__` directories to prevent Python from executing stale cached bytecode.
4. **Resets SQLite Cache**: Wipes cached prompt hashes from `~/.hermes/state.db` so existing sessions rebuild their prompt.
5. **Unlocks 9Router Cooldown**: Clears any active `modelLock_*` locks in `~/.9router/db/data.sqlite` caused by previous 429 backoffs.
6. **Restarts Gateway**: Safely restarts the `hermes gateway` background service (`ai.hermes.gateway`).
7. **Verifies Connectivity**: Runs a live test prompt to ensure end-to-end communication works.

---

## ⚡ Quick Start

### 1-Liner (Local)
```bash
bash /Users/dlir/code/hermes-patch/patch.sh
```

### 1-Liner (Remote via Curl)
```bash
curl -fsSL https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.sh | bash
```

---

## 📖 CLI Usage & Options

```bash
cd /Users/dlir/code/hermes-patch
./patch.sh [OPTIONS]
```

| Flag | Description |
| :--- | :--- |
| `--patch` | Applies the patch (default action) |
| `--check` | Checks if your installation is patched or unpatched without modifying files |
| `--rollback` | Restores files from the most recent automatic backup |
| `--no-restart` | Skips restarting `hermes gateway` |
| `--no-verify` | Skips sending the test query |
| `-h, --help` | Displays help message |

### Environment Variables
- `HERMES_HOME`: Path to custom Hermes installation (defaults to `~/.hermes`).
- `NINE_ROUTER_DB`: Path to custom 9Router database (defaults to `~/.9router/db/data.sqlite`).

---

## 🔄 Rollback / Undo

Every time `./patch.sh` is run, it creates an isolated backup in `~/.hermes/.patch_backup_<timestamp>/`.
To revert your Hermes installation to its previous state:

```bash
./patch.sh --rollback
```

---

## 🧪 Verification

Check your installation status anytime:
```bash
./patch.sh --check
```

Example output:
```text
=================================================================
       Hermes Agent - Google Antigravity / 9Router Patcher       
=================================================================

[INFO] Checking Hermes installation at: /Users/dlir/.hermes
[SUCCESS] SOUL.md: Clean persona detected (PATCHED)
[SUCCESS] prompt_builder.py: Patched in .../environments/151bd1ea.../prompt_builder.py
[SUCCESS] prompt_builder.py: Patched in .../environments/701a1bbc.../prompt_builder.py
[SUCCESS] prompt_builder.py: Patched in .../hermes-agent/agent/prompt_builder.py

[SUCCESS] System status: ALL PATCHES APPLIED
```
