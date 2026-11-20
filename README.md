# Hermes Agent Antigravity / 9Router Compatibility Patch 🚀

A lightweight, automated patch tool for [Hermes Agent](https://github.com/NousResearch/hermes-agent) to work seamlessly with **9Router** and **Google Antigravity / Cloud Code PA** models (e.g. `ag/gemini-3.8-flash`, `gemini-2.5-pro`).

**100% Cross-Platform**: Works natively on **macOS**, **Linux**, and **Windows** (PowerShell, CMD, Git Bash, WSL).

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
This error is **not** a real quota exhaustion. Google Cloud Code PA actively filters system prompts containing verbatim phrases originating from Anthropic Claude Code and OpenCode:
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

### 🚀 Cách 1: Chạy ngay 1 dòng lệnh (KHÔNG cần clone repo)

Chỉ cần mở Terminal / PowerShell lên và dán 1 dòng lệnh duy nhất:

**🍎 macOS / 🐧 Linux / 💻 Git Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.sh | bash
```

**🪟 Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.ps1 | iex
```

*Hoặc chạy trực tiếp bằng Python 1-liner (mọi hệ điều hành):*
```bash
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.py').read().decode('utf-8'))"
```

---

### 📦 Cách 2: Clone repository về máy

#### 🍎 macOS / 🐧 Linux / 💻 Git Bash:
```bash
git clone https://github.com/dlir2404/hermes-patch.git
cd hermes-patch
./patch.sh
# hoặc: python3 patch.py
```

#### 🪟 Windows (PowerShell hoặc CMD):
```powershell
git clone https://github.com/dlir2404/hermes-patch.git
cd hermes-patch
.\patch.ps1
# hoặc: python patch.py
```

---

## 📖 CLI Usage & Options

All scripts (`patch.py`, `patch.sh`, `patch.ps1`) support the same flags:

| Flag | Description |
| :--- | :--- |
| `--patch` | Applies the patch (default action) |
| `--check` | Checks if your installation is patched or unpatched without modifying files |
| `--rollback` | Restores files from the most recent automatic backup |
| `--no-restart` | Skips restarting `hermes gateway` |
| `--no-verify` | Skips sending the test query |
| `-h, --help` | Displays help message |

### Environment Variables & Custom Paths
- `HERMES_HOME`: Path to custom Hermes installation (defaults to `~/.hermes` on Unix, `%USERPROFILE%\.hermes` on Windows).
- `NINE_ROUTER_DB`: Path to custom 9Router database (defaults to `~/.9router/db/data.sqlite` on Unix, `%USERPROFILE%\.9router\db\data.sqlite` on Windows).

---

## 🔄 Rollback / Undo

Every time the patcher runs, it creates an isolated backup in `~/.hermes/.patch_backup_<timestamp>/`.
To revert your Hermes installation to its previous state:

```bash
# macOS / Linux
./patch.sh --rollback
# or
python3 patch.py --rollback

# Windows
.\patch.ps1 -Rollback
# or
python patch.py --rollback
```

---

## 🧪 Verification

Check your installation status anytime:

```bash
# macOS / Linux
python3 patch.py --check

# Windows
python patch.py --check
```

Example output:
```text
=================================================================
       Hermes Agent - Google Antigravity / 9Router Patcher       
              Cross-Platform (Windows, Mac, Linux)               
=================================================================

[INFO] Checking Hermes installation at: ~/.hermes
[SUCCESS] SOUL.md: Clean persona detected (PATCHED)
[SUCCESS] prompt_builder.py: Patched in .../environments/151bd1ea.../prompt_builder.py
[SUCCESS] prompt_builder.py: Patched in .../environments/701a1bbc.../prompt_builder.py
[SUCCESS] prompt_builder.py: Patched in .../hermes-agent/agent/prompt_builder.py

[SUCCESS] System status: ALL PATCHES APPLIED
```
