#!/usr/bin/env bash
# Coulomb Excitation Lab - Linux launcher.
#
# Run ./start_linux.sh in a terminal from this folder (or from anywhere with its full path).
# First start: creates a private Python environment (.venv) and installs the pinned packages (internet needed).
# Later starts: run offline and open the app at http://localhost:8501. Stop with Ctrl+C.
# Extra arguments are passed to run.py, for example:  ./start_linux.sh --test   or   --verify --full

cd "$(dirname "$0")" || exit 1

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
    echo "Install it with your package manager, for example:"
    echo "  Ubuntu 24.04 or newer:  sudo apt install python3 python3-venv"
    echo "  Fedora:                 sudo dnf install python3"
    echo "  Arch:                   sudo pacman -S python"
    echo "or from https://www.python.org/downloads/, then run this script again."
    exit 1
fi

version="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
# Debian and Ubuntu ship venv/ensurepip separately; without them the environment cannot be created.
if [ ! -x .venv/bin/python ] && ! "$PYTHON" -c 'import ensurepip, venv' 2>/dev/null; then
    echo "Python $version is installed, but its 'venv' module is missing, so the environment cannot be created."
    echo "On Debian/Ubuntu install it with:  sudo apt install python$version-venv"
    echo "then run this script again."
    exit 1
fi

echo "Using $("$PYTHON" -c 'import sys; print(sys.executable)') (Python $version)"
exec "$PYTHON" run.py "$@"
