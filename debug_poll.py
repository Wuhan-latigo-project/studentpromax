#!/usr/bin/env python3
"""Standalone Poll loader diagnostic for source and compiled distributions.

Run from the application directory:
    python debug_poll.py

For a Nuitka build, run it beside the executable. It writes poll_debug.log
and reports exactly which path/import/class/constructor step fails.
"""
from __future__ import annotations

import importlib.util
import os
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path

LOG = Path(__file__).resolve().with_name("poll_debug.log")


def log(message: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    LOG.write_text("", encoding="utf-8")
    base = Path(__file__).resolve().parent
    poll_dir = base / "poll"
    poll_path = poll_dir / "poll.py"

    log("=== Poll diagnostic started ===")
    log(f"Python: {sys.version}")
    log(f"Platform: {platform.platform()}")
    log(f"Executable: {sys.executable}")
    log(f"Frozen: {getattr(sys, 'frozen', False)}")
    log(f"__file__: {__file__}")
    log(f"base directory: {base}")
    log(f"poll directory: {poll_dir} exists={poll_dir.exists()}")
    log(f"poll.py: {poll_path} exists={poll_path.exists()}")

    if not poll_path.exists():
        log("FAIL: poll/poll.py is missing from this distribution")
        return 2

    try:
        log(f"poll.py size: {poll_path.stat().st_size} bytes")
        log(f"sys.path before import: {sys.path}")
        if str(poll_dir) not in sys.path:
            sys.path.insert(0, str(poll_dir))
        log(f"sys.path after adding poll directory: {sys.path}")

        spec = importlib.util.spec_from_file_location("poll_debug_module", poll_path)
        log(f"module spec created: {spec}")
        if spec is None or spec.loader is None:
            log("FAIL: importlib could not create a loader")
            return 3

        module = importlib.util.module_from_spec(spec)
        log("module object created; executing poll.py...")
        spec.loader.exec_module(module)
        log("poll.py executed successfully")
        log(f"module classes: {[n for n, v in vars(module).items() if isinstance(v, type)]}")

        student_window = getattr(module, "StudentWindow", None)
        log(f"StudentWindow found: {student_window!r}")
        if student_window is None:
            log("FAIL: StudentWindow class is not available")
            return 4

        log("Import/class check passed. QApplication construction is intentionally not run here.")
        log("=== Poll diagnostic finished successfully ===")
        return 0
    except Exception as exc:
        log(f"FAIL: {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
