# Contributing

Thank you for helping improve the Coulomb Excitation Lab.

## Set up

Start the app with the script for your system (`start_mac.command`, `start_windows.bat` or `./start_linux.sh`); see the [README](README.md). Run the tests before proposing a change:

```sh
python3 run.py --test
```

## Guidelines

- **Physics changes** must cite a source and come with a benchmark or test against published theory or data. See `coulex/literature.py` and `tests/`.
- **Examples** are built from cited literature in `coulex/examples.py`. Do not add data from TCLX or any other unlicensed code.
- **Interface text** must have a Greek translation in `coulex/i18n_el.py`; `tests/test_ui_modes.py` checks coverage.
- **Licensing:** contributions are accepted under the GNU GPL v3 (see [LICENSE](LICENSE)). Only submit code you have the right to license that way.

## Pull requests

1. Describe what changed and why.
2. Include or update tests; keep `python3 run.py --test` passing.
3. Keep unrelated changes in separate pull requests.

## Reporting problems

Open an issue using the bug report or feature request template. For numerical disagreements, include the reaction input, the angle and the output you expected, with its source.
