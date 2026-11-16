"""The double-click launchers stay consistent with run.py and keep working line endings."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = 'sys.exit(not (3, 12) <= sys.version_info[:2] < (3, 15))'


def test_launchers_call_run_py_and_accept_the_same_python_versions():
    mac = (ROOT/'start_mac.command').read_text()
    linux = (ROOT/'start_linux.sh').read_text()
    windows = (ROOT/'start_windows.bat').read_bytes().decode('ascii')
    assert '"$PYTHON" run.py "$@"' in mac and '"$PYTHON" run.py "$@"' in linux and '%PYTHON% run.py %*' in windows
    assert all(VERSIONS in text for text in (mac, linux, windows))
    assert 'if not (3, 12) <= sys.version_info[:2] < (3, 15):' in (ROOT/'run.py').read_text()
    assert all(f'python{v}' in mac and f'python{v}' in linux for v in ('3.12', '3.13', '3.14'))
    assert '(3.14 3.13 3.12)' in windows
    assert 'import ensurepip, venv' in linux  # Debian/Ubuntu ship venv separately


def test_launcher_files_are_runnable_on_their_systems():
    for name in ('start_mac.command', 'start_linux.sh'):
        script = ROOT/name
        assert os.access(script, os.X_OK) and b'\r' not in script.read_bytes()
        assert subprocess.run(['bash', '-n', str(script)]).returncode == 0
    windows = (ROOT/'start_windows.bat').read_bytes()
    assert windows.count(b'\n') == windows.count(b'\r\n')  # CRLF only
    attributes = (ROOT/'.gitattributes').read_text()
    assert '*.bat text eol=crlf' in attributes and '*.command text eol=lf' in attributes
