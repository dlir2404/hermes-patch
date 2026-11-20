<div align="center">

# hermes-patch

**Automated patch tool for Hermes Agent to seamlessly connect with 9Router and Google Antigravity / Gemini models.**

![platform: macOS · Linux · Windows](https://img.shields.io/badge/platform-macOS%20%C2%B7%20Linux%20%C2%B7%20Windows-blue)
![python: >=3.8](https://img.shields.io/badge/python-%3E%3D3.8-brightgreen)
[![license: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-support-FF5E5B?logo=kofi&logoColor=white)](https://ko-fi.com/dlir2404)

[Overview](#overview) · [Quick Start](#quick-start) · [What It Fixes](#what-it-fixes) · [CLI Options](#cli-options) · [Rollback](#rollback)

</div>

---

## Overview

When using [Hermes Agent](https://github.com/NousResearch/hermes-agent) with **9Router** or **Google Antigravity / Cloud Code PA** models (such as `ag/gemini-3.8-flash` or `gemini-2.5-pro`), upstream safety filters reject requests with an unexpected HTTP 429 status code.

This issue occurs because stock prompt templates inside Hermes contain specific phrasing patterns that trigger upstream policy checks.

**`hermes-patch`** automatically resolves this by:
- Updating persona definitions across all `SOUL.md` files and default templates to clean, optimized directives.
- Sanitizing prompt builder constants in the core repository and all virtual environment workspaces.
- Purging compiled Python bytecode caches (`__pycache__` and `*.pyc`).
- Invalidating stale system prompt hashes stored in `state.db`.
- Resetting model cooldown locks in 9Router if present.
- Restarting the background gateway service cleanly.

Works out of the box with **zero extra dependencies** on **macOS**, **Linux**, and **Windows**.

---

## Quick Start

### Option 1: One-Line Run (No clone needed)

Run directly from your terminal or console without cloning this repository:

**macOS / Linux / Git Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.ps1 | iex
```

**Any OS with Python:**
```bash
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/dlir2404/hermes-patch/main/patch.py').read().decode('utf-8'))"
```

---

### Option 2: Clone & Run Locally

**macOS / Linux:**
```bash
git clone https://github.com/dlir2404/hermes-patch.git
cd hermes-patch
./patch.sh
# or: python3 patch.py
```

**Windows (PowerShell or CMD):**
```powershell
git clone https://github.com/dlir2404/hermes-patch.git
cd hermes-patch
.\patch.ps1
# or: python patch.py
```

---

## What It Fixes

1. **Persona Files (`SOUL.md`)**: Rewrites the agent persona in `~/.hermes/SOUL.md`, profiles, and default templates with clean, direct instructions compatible with Google Gemini models.
2. **Template Generators (`default_soul.py`)**: Updates the built-in generator template so any newly created Hermes profiles stay compatible.
3. **Core Prompt Builders (`prompt_builder.py`, `system_prompt.py`)**: Sanitizes identity constants, execution guidance, and operational directive headers across the main codebase and runtime workspaces (`~/.hermes/installs/*/environments/*/workspace/`).
4. **Bytecode Cache Purge**: Cleans up all `*.pyc` and `__pycache__` artifacts to force Python to recompile clean bytecode.
5. **Session Cache Invalidation**: Clears cached prompt hashes in `~/.hermes/state.db` so existing sessions rebuild their prompt context.
6. **9Router Cooldown Reset**: Removes backoff lock flags from `~/.9router/db/data.sqlite` caused by previous 429 errors.
7. **Gateway Service Refresh**: Safely executes `hermes gateway restart -y` to reload the background service.

---

## CLI Options

All entry points (`patch.py`, `patch.sh`, `patch.ps1`) support the following flags:

| Flag | Description |
| :--- | :--- |
| `--patch` | Applies the compatibility patches (default action) |
| `--check` | Verifies current installation status without modifying any files |
| `--rollback` | Restores files from the most recent automatic backup |
| `--no-restart` | Skips restarting the background gateway service |
| `--no-verify` | Skips running the post-patch test query |
| `-h, --help` | Shows help message and exits |

### Custom Paths & Environment Variables
- `HERMES_HOME` (or `--hermes-dir`): Path to custom Hermes directory (default: `~/.hermes` or `%USERPROFILE%\.hermes`).
- `NINE_ROUTER_DB` (or `--router-db`): Path to 9Router SQLite database (default: `~/.9router/db/data.sqlite`).

---

## Rollback

Before modifying any file, an isolated backup is created at `~/.hermes/.patch_backup_<timestamp>/`.
To revert to your previous configuration at any time:

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

## Verification

Check your system status at any time:

```bash
python3 patch.py --check
```

Example status report:
```text
=================================================================
       Hermes Agent - Google Antigravity / 9Router Patcher       
              Cross-Platform (Windows, Mac, Linux)               
=================================================================

[INFO] Checking Hermes installation at: ~/.hermes
[SUCCESS] SOUL.md: Clean persona detected in ~/.hermes/SOUL.md
[SUCCESS] default_soul.py: Patched in .../hermes_cli/default_soul.py
[SUCCESS] prompt_builder.py: Patched in .../agent/prompt_builder.py

[SUCCESS] System status: ALL PATCHES APPLIED
```

---

## Support

If this tool helped you, feel free to support:

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-support-FF5E5B?logo=kofi&logoColor=white)](https://ko-fi.com/dlir2404)

---

## License

[MIT](LICENSE)
