# TCLX comparison inputs (not distributed)

The archived comparison in `../results/` was computed from the two example inputs of
[TCLX by J. Henderson](https://github.com/jhenderson88/TCLX). TCLX carries no licence, so these
files are **not distributed** with this project and are ignored by git.

To rerun the comparison, download them into this folder:

```sh
curl -L -o validation/tclx_inputs/22Mg_104Pd_example.txt https://raw.githubusercontent.com/jhenderson88/TCLX/master/22Mg_104Pd_example.txt
curl -L -o validation/tclx_inputs/80Sr_208Pb_example.txt https://raw.githubusercontent.com/jhenderson88/TCLX/master/80Sr_208Pb_example.txt
```

Verification accepts them only if their SHA-256 hashes match the archived manifest:

| File | SHA-256 |
|---|---|
| `22Mg_104Pd_example.txt` | `f90351b12e9742eb23cb041eea8d925518c19e0a824e591fbdba8a4653d7482c` |
| `80Sr_208Pb_example.txt` | `713a8ae0df73b03f6fe441fdbf6f05890f725b9e664f7ede2a863619ec916022` |

Without them, `python3 run.py --verify` stops with these instructions and the tests that need them are skipped.
All other tests, the literature benchmarks and the archived report do not need them.

`recorded_output/` (also git-ignored) may hold the full text that TCLX printed for the archived run. It is kept
locally for reference only; the numbers used by the comparison are in `../results/comparison.csv`.
