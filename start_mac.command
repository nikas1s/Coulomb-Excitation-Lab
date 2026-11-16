#!/bin/bash
# Coulomb Excitation Lab - macOS launcher.
#
# Double-click this file in Finder, or run ./start_mac.command in Terminal.
# First start: creates a private Python environment (.venv) and installs the pinned packages (internet needed).
# Later starts: run offline and open the app at http://localhost:8501. Stop with Ctrl+C.
# Extra arguments are passed to run.py, for example:  ./start_mac.command --test   or   --verify --full

cd "$(dirname "$0")" || exit 1

# Finder-started windows may miss the usual install locations of Homebrew and python.org.
PATH="$PATH:/opt/homebrew/bin:/usr/local/bin"
for version in 3.14 3.13 3.12; do
    PATH="$PATH:/Library/Frameworks/Python.framework/Versions/$version/bin"
done
export PATH

pause() {
    if [ -t 0 ]; then
        read -r -p "Press Enter to close this window..." _
    fi
}

PYTHON=""
for candidate in python3.14 python3.13 python3.12 python3; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(not (3, 12) <= sys.version_info[:2] < (3, 15))' 2>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3.12, 3.13 or 3.14 is needed but was not found."
    echo "Install it from https://www.python.org/downloads/macos/ (or with Homebrew: brew install python@3.13),"
    echo "then double-click this file again."
    pause
    exit 1
fi

echo "Using $("$PYTHON" -c 'import sys; print(sys.executable, sys.version.split()[0])')"
"$PYTHON" run.py "$@"
status=$?
if [ "$status" -ne 0 ]; then
    echo
    echo "The launcher stopped with an error (code $status). See the messages above."
    pause
fi
exit "$status"
