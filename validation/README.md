# Numerical comparison with TCLX

Adaptation credit: [TCLX](https://github.com/jhenderson88/TCLX) and [Cygnus](https://github.com/jhenderson88/Cygnus) by J. Henderson. Only numerical comparison data, citations and reports are retained. The original source, copied source snapshots, ROOT adapter and compiled executable have been removed. TCLX has no licence, so its two comparison inputs are not distributed: download them into [`tclx_inputs/`](tclx_inputs/README.md) to rerun the comparison.

The two comparison inputs use matched settings, including `polarization_convention="reference"`. The app defaults to `standard`, which uses the excited nucleus in the literature polarization formula. Its polarized results therefore differ from this matched-setting comparison. The tested cases cover E2 projectile excitation from a spin-zero ground state.

## Check the current Python implementation

First download the two TCLX inputs into `tclx_inputs/` ([instructions](tclx_inputs/README.md)); their hashes are checked. Without them, `--verify` stops with these instructions and the regression tests that need them are skipped. `--inputs DIR` reads them from another folder. Then, from the application folder:

```sh
python3 run.py --verify --full
python3 run.py --test
```

These commands run entirely in Python. No compiler or ROOT installation is needed. `--full` checks all 180 integer CM angles for each input; without it, ten representative angles are checked. Verification also repeats tighter-tolerance, longer-orbit and independent-integrator convergence checks.

New outputs go to **`current/`**: comparison CSV, convergence CSV, run manifest, report and residual plot. These generated files are updated on subsequent runs. The archived evidence in **`results/`** remains unchanged. The application displays the archived comparison; open `current/REPORT.md` for the latest command-line run.

This checks Python against **previously recorded outputs**; it cannot regenerate reference-program outputs without obtaining the cited project separately.

## Archived evidence

- `results/REPORT.md` and `results/original_comparison.png`: historical summary and residual plot.
- `results/comparison.csv`: probabilities and cross sections for every level/angle.
- `results/convergence.csv`: numerical convergence results at the time of the comparison.
- `results/manifest.json`: historical model settings, source/input hashes, platform and versions.
- The full text output printed by TCLX is not distributed; `comparison.csv` keeps its probabilities and cross sections.
- `results/checksums.json`: SHA-256 hashes protecting the archived artifacts against accidental changes.

The historical reference was executed with a tested minimal ROOT compatibility adapter, not a complete ROOT/GSL installation. Hashes of the removed source are kept solely as comparison provenance. Verification checks archive integrity and matching input hashes before any calculation.

The regression tolerance is `1e-6 + 2e-5*|P_reference|`; each numerical convergence check targets a maximum absolute population change below `1e-7`. These are test thresholds, not physical uncertainty estimates. Very small populations require a separate relative-accuracy assessment. Independent scientific benchmarks remain in `coulex/literature.py` and the application's Verification tab.
