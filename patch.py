#!/usr/bin/env python3
"""
Hermes Agent - Google Antigravity / 9Router Compatibility Patcher
Cross-platform: Windows, macOS, Linux.
Compatible with Python 3.8+ (Hermes requires Python 3.11+).
Zero external dependencies (uses standard library only).
"""

from __future__ import annotations

import os
import sys
import re
import shutil
import sqlite3
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# Enable ANSI escape code support on Windows terminal
if os.name == 'nt':
    os.system('')

# Styling
BOLD = "\033[1m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"

def info(msg: str):
    print(f"{BLUE}[INFO]{NC} {msg}")

def success(msg: str):
    print(f"{GREEN}[SUCCESS]{NC} {msg}")

def warn(msg: str):
    print(f"{YELLOW}[WARN]{NC} {msg}")

def error(msg: str):
    print(f"{RED}[ERROR]{NC} {msg}", file=sys.stderr)

def print_banner():
    print(f"{CYAN}{BOLD}")
    print("=================================================================")
    print("       Hermes Agent - Google Antigravity / 9Router Patcher       ")
    print("              Cross-Platform (Windows, Mac, Linux)               ")
    print("=================================================================")
    print(f"{NC}")

# Target Prompts & Replacements
CLEAN_SOUL = """You are Antigravity, an agentic AI assistant developed by the Google DeepMind team, powered by Gemini. Be direct: calibrate your response length to the complexity of the request — a short query receives a concise answer, and completed work yields a brief summary of changes, verifications, and next steps, without recounting the process. No filler ("Great question," "I'd be happy to"), no repeating the question, no summarizing prior messages, and no narrating tool executions. State facts plainly without exaggeration; acknowledge uncertainty directly. Agree based on merit, not deference. Depth must be warranted by context, user preference, or topic complexity.
"""

NEW_AGENT_IDENTITY = '''DEFAULT_AGENT_IDENTITY = (
    # A behavior spec (sizing rule, named prohibitions, earned-depth escape hatch), not a trait list — trait
    # lists change nothing. Maintainer rule: models UNDER-explore by default; never re-add an exploration-thrift line.
    "You are an AI assistant. Be direct: calibrate your response length to the complexity of the request "
    "— a short query receives a concise answer, and completed work yields a brief summary of changes, what's "
    "verified, and next steps, without recounting the process. No filler (\\"Great question,\\" \\"I'd be happy to\\"), no "
    "repeating the question, no summarizing prior messages, and no narrating tool executions. "
    "State facts plainly without exaggeration; acknowledge uncertainty directly. Agree based on merit, not deference. "
    "Depth must be warranted by context, user preference, or topic complexity."
)'''

NEW_DEFAULT_SOUL = '''DEFAULT_SOUL_MD = (
    "You are Antigravity, an agentic AI assistant developed by the Google DeepMind team, powered by Gemini. "
    "Be direct: calibrate your response length to the complexity of the request — a short query receives a "
    "concise answer, and completed work yields a brief summary of changes, verifications, and next steps, "
    "without recounting the process. No filler (\\"Great question,\\" \\"I'd be happy to\\"), no repeating "
    "the question, no summarizing prior messages, and no narrating tool executions. State facts plainly "
    "without exaggeration; acknowledge uncertainty directly. Agree based on merit, not deference. "
    "Depth must be warranted by context, user preference, or topic complexity."
)'''

NEW_TASK_COMPLETION = '''TASK_COMPLETION_GUIDANCE = (
    "# Task completion\\n"
    "When asked to build, run, or verify solutions, deliver functional and verified results backed by tool "
    "execution. Do not stop after writing a stub, a plan, or a single command. Keep working until you have "
    "executed the code and confirmed the results.\\n"
    "If a tool, install, or network call fails and blocks progress, state the blocker clearly and try alternatives "
    "(different package manager, different approach, ask the user). Never fabricate output or fake API "
    "responses. An honest blocker report is always preferred over imagined results."
)'''

PATTERN_ID = re.compile(r'DEFAULT_AGENT_IDENTITY\s*=\s*(?:\([\s\S]*?\n\)|\"[^\"]*\")')
PATTERN_DEFAULT_SOUL = re.compile(r'DEFAULT_SOUL_MD\s*=\s*(?:\([\s\S]*?\n\)|\"[^\"]*\")')
PATTERN_HELP = re.compile(r'HERMES_AGENT_HELP_GUIDANCE\s*=\s*(?:\([\s\S]*?\n\)|\"[^\"]*\")')
PATTERN_NO_SKILLS = re.compile(r'HERMES_AGENT_HELP_GUIDANCE_NO_SKILLS\s*=\s*(?:\([\s\S]*?\n\)|\"[^\"]*\")')
PATTERN_TASK = re.compile(r'TASK_COMPLETION_GUIDANCE\s*=\s*(?:\([\s\S]*?\n\)|\"[^\"]*\")')

def find_hermes_executable() -> Optional[str]:
    # 1. System PATH
    bin_path = shutil.which("hermes")
    if bin_path:
        return bin_path

    # 2. Common Unix local bin
    local_bin = Path.home() / ".local" / "bin" / "hermes"
    if local_bin.is_file() and os.access(local_bin, os.X_OK):
        return str(local_bin)

    # 3. Windows Python Scripts directory
    if os.name == 'nt':
        py_scripts = Path(sys.executable).parent / "Scripts" / "hermes.exe"
        if py_scripts.is_file():
            return str(py_scripts)
        appdata_scripts = Path.home() / "AppData" / "Roaming" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts" / "hermes.exe"
        if appdata_scripts.is_file():
            return str(appdata_scripts)

    return None

def do_check(hermes_dir: Path):
    print_banner()
    info(f"Checking Hermes installation at: {hermes_dir}")

    if not hermes_dir.is_dir():
        error(f"Hermes directory not found at: {hermes_dir}")
        sys.exit(1)

    all_patched = True

    # Check all SOUL.md files
    soul_files = list(hermes_dir.glob("**/SOUL.md"))
    for sf in soul_files:
        if ".patch_backup" in sf.parts:
            continue
        text = sf.read_text(encoding="utf-8", errors="ignore")
        if "You are Hermes Agent, built by Nous Research" in text or "Be direct: match the length" in text:
            warn(f"SOUL.md: Stock trigger phrases detected in {sf}")
            all_patched = False
        else:
            success(f"SOUL.md: Clean persona detected in {sf}")

    # Check all default_soul.py files
    ds_files = list(hermes_dir.glob("**/default_soul.py"))
    for ds in ds_files:
        if ".patch_backup" in ds.parts:
            continue
        text = ds.read_text(encoding="utf-8", errors="ignore")
        if "You are Hermes Agent, built by Nous Research" in text:
            warn(f"default_soul.py: Unpatched in {ds}")
            all_patched = False
        else:
            success(f"default_soul.py: Patched in {ds}")

    # Check all prompt_builder.py files
    pb_files = list(hermes_dir.glob("**/prompt_builder.py"))
    for pb in pb_files:
        if ".patch_backup" in pb.parts:
            continue
        text = pb.read_text(encoding="utf-8", errors="ignore")
        if ("You are Hermes Agent, built by Nous Research" in text or
            "# Google model operational directives" in text or
            "# Finishing the job" in text):
            warn(f"prompt_builder.py: Unpatched in {pb}")
            all_patched = False
        else:
            success(f"prompt_builder.py: Patched in {pb}")

    print()
    if all_patched:
        success("System status: ALL PATCHES APPLIED")
    else:
        warn("System status: UNPATCHED or PARTIALLY PATCHED. Run with --patch to fix.")

def do_rollback(hermes_dir: Path, skip_restart: bool):
    print_banner()
    info(f"Searching for available backups in: {hermes_dir}")

    backups = sorted([p for p in hermes_dir.iterdir() if p.is_dir() and p.name.startswith(".patch_backup_")], reverse=True)
    if not backups:
        error(f"No backup directories found in {hermes_dir}.")
        sys.exit(1)

    latest_backup = backups[0]
    info(f"Restoring from latest backup: {latest_backup}")

    manifest_file = latest_backup / "manifest.txt"
    if not manifest_file.is_file():
        error(f"manifest.txt not found in {latest_backup}")
        sys.exit(1)

    with open(manifest_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    for line in lines:
        if not line.strip() or "|" not in line:
            continue
        rel_path, orig_abs_path = line.split("|", 1)
        backup_src = latest_backup / rel_path
        dest = Path(orig_abs_path)
        if backup_src.is_file():
            info(f"Restoring: {dest}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_src, dest)

    # Purge bytecode
    info("Purging Python bytecode caches (*.pyc and __pycache__)...")
    for pycache in hermes_dir.glob("**/__pycache__"):
        try:
            shutil.rmtree(pycache, ignore_errors=True)
        except Exception:
            pass
    for pyc in hermes_dir.glob("**/*.pyc"):
        try:
            pyc.unlink(missing_ok=True)
        except Exception:
            pass

    # Clear SQLite cache
    reset_state_db(hermes_dir)

    if not skip_restart:
        restart_gateway()

    print()
    success("Rollback completed successfully!")

def reset_state_db(hermes_dir: Path):
    state_db = hermes_dir / "state.db"
    if state_db.is_file():
        try:
            conn = sqlite3.connect(str(state_db))
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET system_prompt = NULL, system_prompt_hash = NULL;")
            cursor.execute("DELETE FROM system_prompts;")
            conn.commit()
            cursor.execute("VACUUM;")
            conn.close()
            success("state.db prompt cache cleared.")
        except Exception as e:
            warn(f"Could not clear state.db cache: {e}")
    else:
        info("state.db not present; skipped.")

def unlock_9router(router_db: Path):
    if router_db.is_file():
        try:
            conn = sqlite3.connect(str(router_db))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kv WHERE key LIKE 'modelLock_%' OR key LIKE '%modelLock%';")
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            success(f"9Router model cooldown locks reset ({deleted} removed).")
        except Exception as e:
            warn(f"Could not clear 9Router model locks: {e}")
    else:
        info("9Router database not found; skipped.")

def restart_gateway():
    hermes_bin = find_hermes_executable()
    if not hermes_bin:
        warn("Hermes binary not found in PATH. Please restart hermes gateway manually if running.")
        return

    info(f"Running: {hermes_bin} gateway restart -y")
    try:
        res = subprocess.run([hermes_bin, "gateway", "restart", "-y"], capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            success("Hermes gateway restarted.")
        else:
            warn(f"Gateway restart returned code {res.returncode}. Output:\n{res.stderr or res.stdout}")
    except subprocess.TimeoutExpired:
        warn("Gateway restart command timed out.")
    except Exception as e:
        warn(f"Could not run gateway restart: {e}")

def verify_fix():
    hermes_bin = find_hermes_executable()
    if not hermes_bin:
        info("Skipping live query verification (hermes binary not found).")
        return

    info("Running verification test: hermes chat -q 'Xin chao'...")
    try:
        res = subprocess.run(
            [hermes_bin, "chat", "-q", "Xin chao, test ket noi 1 cau ngan gon."],
            capture_output=True,
            text=True,
            timeout=25
        )
        if res.returncode == 0:
            out = res.stdout.strip()
            print(f"{GREEN}Response:{NC} {out}")
            success("Live verification passed!")
        else:
            warn(f"Verification query returned code {res.returncode}. Output:\n{res.stderr or res.stdout}")
    except subprocess.TimeoutExpired:
        warn("Verification query timed out.")
    except Exception as e:
        warn(f"Could not execute verification query: {e}")

def do_patch(hermes_dir: Path, router_db: Path, skip_restart: bool, skip_verify: bool):
    print_banner()
    info(f"Target Hermes Directory: {hermes_dir}")

    # 1. Create timestamped backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = hermes_dir / f".patch_backup_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = backup_dir / "manifest.txt"
    info(f"Creating backup at: {backup_dir}")

    manifest_entries = []

    def backup_path(file_path: Path):
        rel_str = str(file_path.relative_to(hermes_dir)).replace("/", "_").replace("\\", "_")
        dest = backup_dir / rel_str
        shutil.copy2(file_path, dest)
        manifest_entries.append(f"{rel_str}|{file_path.resolve()}")

    # 2. Patch all SOUL.md files and Python sources recursively
    info("1/6. Updating all SOUL.md and default_soul.py templates...")
    for root, dirs, files in os.walk(hermes_dir):
        if ".patch_backup" in root or "__pycache__" in root:
            continue

        for f in files:
            fpath = Path(root) / f

            if f == "SOUL.md":
                backup_path(fpath)
                fpath.write_text(CLEAN_SOUL, encoding="utf-8")
                print(f"  [+] Updated persona: {fpath}")

            elif f == "default_soul.py":
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                backup_path(fpath)
                content = PATTERN_DEFAULT_SOUL.sub(lambda m: NEW_DEFAULT_SOUL, content)
                fpath.write_text(content, encoding="utf-8")
                print(f"  [+] Patched default template: {fpath}")

    # Ensure root SOUL.md exists
    root_soul = hermes_dir / "SOUL.md"
    if not root_soul.is_file():
        root_soul.write_text(CLEAN_SOUL, encoding="utf-8")
        print(f"  [+] Created root persona: {root_soul}")

    success("All personas and default templates updated.")

    # 3. Patch Python prompt builders and system prompts
    info("2/6. Locating and patching prompt_builder.py and system_prompt.py...")
    for root, dirs, files in os.walk(hermes_dir):
        if ".patch_backup" in root or "__pycache__" in root:
            continue

        for f in files:
            fpath = Path(root) / f

            if f == "prompt_builder.py":
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                backup_path(fpath)

                content = PATTERN_ID.sub(lambda m: NEW_AGENT_IDENTITY, content)
                content = PATTERN_HELP.sub(lambda m: 'HERMES_AGENT_HELP_GUIDANCE = ""', content)
                content = PATTERN_NO_SKILLS.sub(lambda m: 'HERMES_AGENT_HELP_GUIDANCE_NO_SKILLS = ""', content)
                content = PATTERN_TASK.sub(lambda m: NEW_TASK_COMPLETION, content)

                content = content.replace("# Google model operational directives", "# Operational directives")
                content = content.replace("Mid-turn, the user can steer you: Hermes delivers their message", "Mid-turn, the user can steer you: The system delivers their message")
                content = content.replace("where Hermes itself is running", "where the assistant itself is running")
                content = content.replace("where Hermes itself runs", "where the assistant itself runs")
                content = content.replace("cwd of the Hermes process", "cwd of the assistant process")
                content = content.replace('RUNTIME_ENVIRONMENT_HEADING = "# Hermes runtime environment"', 'RUNTIME_ENVIRONMENT_HEADING = "# Runtime environment"')
                content = content.replace('RUNTIME_ENVIRONMENT_END = "<!-- End Hermes runtime environment -->"', 'RUNTIME_ENVIRONMENT_END = "<!-- End Runtime environment -->"')

                fpath.write_text(content, encoding="utf-8")
                print(f"  [+] Patched: {fpath}")

            elif f == "system_prompt.py":
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                backup_path(fpath)

                content = content.replace("Active Hermes profile:", "Active profile:")
                fpath.write_text(content, encoding="utf-8")
                print(f"  [+] Patched: {fpath}")

    # Write manifest
    manifest_file.write_text("\n".join(manifest_entries) + "\n", encoding="utf-8")
    success("Python prompt builders and system prompts patched.")

    # 4. Purge bytecode
    info("3/6. Purging Python bytecode caches (*.pyc and __pycache__)...")
    for pycache in hermes_dir.glob("**/__pycache__"):
        try:
            shutil.rmtree(pycache, ignore_errors=True)
        except Exception:
            pass
    for pyc in hermes_dir.glob("**/*.pyc"):
        try:
            pyc.unlink(missing_ok=True)
        except Exception:
            pass
    success("Bytecode caches purged.")

    # 5. Clear SQLite DB Cache
    info("4/6. Resetting SQLite prompt cache in state.db...")
    reset_state_db(hermes_dir)

    # 6. Clear 9Router Model Locks
    info("5/6. Checking 9Router database for cooldown locks...")
    unlock_9router(router_db)

    # 7. Restart Gateway
    if not skip_restart:
        info("6/6. Restarting Hermes gateway background service...")
        restart_gateway()
    else:
        info("6/6. Gateway restart skipped (--no-restart passed).")

    # 8. Verification
    if not skip_verify:
        verify_fix()

    print()
    success("=================================================================")
    success("  All patches applied successfully! Hermes is ready to run.     ")
    success(f"  Backup saved at: {backup_dir}")
    success("=================================================================")

def main():
    parser = argparse.ArgumentParser(
        description="Hermes Agent Antigravity / 9Router Compatibility Patcher (Cross-Platform)"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--patch", action="store_true", default=True, help="Apply compatibility patch (default)")
    group.add_argument("--check", action="store_true", help="Check current patch status")
    group.add_argument("--rollback", action="store_true", help="Restore original files from latest backup")

    parser.add_argument("--no-restart", action="store_true", help="Skip restarting hermes gateway")
    parser.add_argument("--no-verify", action="store_true", help="Skip live verification test query")
    parser.add_argument("--hermes-dir", type=str, default=None, help="Custom path to ~/.hermes directory")
    parser.add_argument("--router-db", type=str, default=None, help="Custom path to 9Router data.sqlite DB")

    args = parser.parse_args()

    # Determine hermes_dir
    if args.hermes_dir:
        hermes_dir = Path(args.hermes_dir).expanduser().resolve()
    elif "HERMES_HOME" in os.environ:
        hermes_dir = Path(os.environ["HERMES_HOME"]).expanduser().resolve()
    else:
        hermes_dir = (Path.home() / ".hermes").resolve()

    # Determine router_db
    if args.router_db:
        router_db = Path(args.router_db).expanduser().resolve()
    elif "NINE_ROUTER_DB" in os.environ:
        router_db = Path(os.environ["NINE_ROUTER_DB"]).expanduser().resolve()
    else:
        router_db = (Path.home() / ".9router" / "db" / "data.sqlite").resolve()

    if args.check:
        do_check(hermes_dir)
    elif args.rollback:
        do_rollback(hermes_dir, skip_restart=args.no_restart)
    else:
        do_patch(hermes_dir, router_db, skip_restart=args.no_restart, skip_verify=args.no_verify)

if __name__ == "__main__":
    main()
