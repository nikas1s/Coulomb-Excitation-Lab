#!/usr/bin/env python3
"""One-command launcher: python3 coulex_streamlit/run.py (standard library only)."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def has_pip(python):
    return python.exists() and subprocess.run([str(python), "-m", "pip", "--version"],
                                              capture_output=True).returncode == 0


def create_environment(environment):
    print("Creating an isolated Python environment…", flush=True)
    try:
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
    except (OSError, subprocess.CalledProcessError) as error:
        shutil.rmtree(environment, ignore_errors=True)
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise SystemExit(f"Could not create the Python environment ({error}).\n"
                         f"Python's venv module is probably missing. On Debian/Ubuntu: sudo apt install python{version}-venv\n"
                         "Then run this command again.")


def main():
    if not (3, 12) <= sys.version_info[:2] < (3, 15):
        raise SystemExit("Please install Python 3.12, 3.13, or 3.14, then run this command again.")
    environment = ROOT / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    requirements = ROOT / "requirements.txt"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = environment / ".requirements-sha256"
    # A half-created environment (python without pip) from an earlier failed attempt is rebuilt.
    if not python.exists() or (not marker.exists() and not has_pip(python)):
        create_environment(environment)
    if not marker.exists() or marker.read_text().strip() != digest:
        print("Installing the pinned open-source dependencies (internet needed on first run)…", flush=True)
        subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
                        "--no-cache-dir", "-r", str(requirements)], check=True, cwd=ROOT)
        marker.write_text(digest)
    arguments = sys.argv[1:]
    if arguments and arguments[0] == "--test":
        command = [str(python), "-m", "pytest", "-q", *arguments[1:]]
    elif arguments and arguments[0] == "--qualify":
        command = [str(python), "validation/qualify.py", *arguments[1:]]
    elif arguments and arguments[0] == "--verify":
        command = [str(python), "validation/verify.py", *arguments[1:]]
    else:
        command = [str(python), "-m", "streamlit", "run", "app.py", *arguments]
    try:
        return subprocess.call(command, cwd=ROOT)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"Dependency installation failed ({error.returncode}). Check your network and retry.")
