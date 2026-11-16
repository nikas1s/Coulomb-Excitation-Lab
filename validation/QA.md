# Verification record

Checked on **2026-11-16**, macOS ARM64 / Python 3.14. Dependency versions are pinned in `../requirements.txt`.

## Automated tests

`./start_mac.command --test` passed **103 tests with no skips** in 71 seconds, with the TCLX inputs present; see [tests.log](tests.log). In a fresh clone the three regression tests that need those inputs are skipped with an explanation (see [tclx_inputs/README.md](tclx_inputs/README.md)).

Coverage includes:

- Twelve independent solver benchmarks: Rutherford scattering, weak E1–E4 excitation, the exact two-state sudden limit, and Alder–Winther rotor amplitudes (Table 4) and populations (Table 5); in addition, the solver matches the exact Alder–Winther rotor formula to 2 × 10⁻⁵.
- Polarization for both projectile and target excitation, using the excited nucleus as prescribed by [Orce (2016), Eq. (4) and footnote 1](https://arxiv.org/abs/1510.04087). The model strength is adjustable; formula agreement is not a universal polarizability validation.
- Probability conservation, Hermitian couplings, half-integer initial spins, signed elements, target/projectile equivalence, lab Jacobians, detector integrals and stopping-depth averaging.
- Nuclear and measurement uploads, custom headers, units, uncertainties, count efficiencies, invalid-data errors and stale-result handling.
- English/Greek controls and error messages, input preservation across language changes, empty own-data modes, every example input, instructions and downloadable formats.
- Licensing and distribution: no TCLX input is shipped with the examples, and archived evidence and inputs are hash-checked.
- Start scripts: both stay consistent with `run.py` (supported Python versions, arguments, CRLF line endings for the `.bat`, executable `.command`).

## Start scripts

`start_mac.command` and `start_windows.bat` find Python 3.12–3.14 and call `run.py`, which creates `.venv`, installs the pinned packages and starts the app. Checked on macOS:

- A clean copy without `.venv` or TCLX inputs built its environment from scratch and ran the suite through the launcher, exit code 0; the TCLX regression tests were skipped as intended.
- The app started headless through the launcher and answered its health check.
- With only the system Python 3.9 available, the script printed the install instructions and exited with code 1.

**The Windows script has not been run on Windows.**

## Licensing (GNU GPL v3)

The project is distributed under the GNU GPL v3 (`../LICENSE`, identical to the licence text of [Cygnus](https://github.com/jhenderson88/Cygnus)). README, notices, the solver and the app's Guide credit TCLX and Cygnus by J. Henderson and state the modifications; `../THIRD_PARTY_NOTICES.md` maps every adapted component to its GPL-3.0 Cygnus counterpart.

TCLX has no licence. Its source, build tools, ROOT adapter and executable were removed after the comparison. Its two example inputs and the full text it printed are kept only in the git-ignored `tclx_inputs/` folder (download instructions and hashes in [tclx_inputs/README.md](tclx_inputs/README.md)); `results/comparison.csv` keeps the compared numbers. All built-in examples were written for this project from cited literature.

## Literature and example data

Reference tables and numerical inputs were checked against primary sources:

- [Alder & Winther (1960), Tables 4 and 5](https://gymarkiv.sdu.dk/MFM/kdvs/mfm%2030-39/mfm-32-8.pdf).
- [Pritychenko et al. (2016), Table 3](https://arxiv.org/abs/1312.5975).
- ENSDF adopted levels and moments for [22Mg](https://www.nndc.bnl.gov/ensnds/22/Mg/adopted.pdf), [58Ni](https://www.nndc.bnl.gov/ensnds/58/Ni/adopted.pdf), [152Sm](https://www.nndc.bnl.gov/ensnds/152/Sm/adopted.pdf), [208Pb](https://www.nndc.bnl.gov/ensnds/208/Pb/adopted.pdf) and [238U](https://www.nndc.bnl.gov/ensnds/238/U/adopted.pdf).

Examples distinguish evaluated inputs from derived rigid-rotor elements. Small highest-level populations and the 5 fm separation guideline are diagnostics, not proofs of model completeness or physical validity.

## Code comparison

Before source removal, the reference-generation run passed for both TCLX comparison inputs at 180 angles each: **360 collisions, 2,520 level/angle records**. Maximum absolute probability difference: **6.26217e-7**. Tighter-tolerance, longer-orbit and independent-integrator checks also passed. See [REPORT.md](results/REPORT.md), [manifest.json](results/manifest.json) and [verification.log](verification.log).

`--verify` now evaluates only Python against the saved numerical data. It validates archive and input hashes and writes to `current/`, leaving `results/` intact. The latest `--verify --full` run passed with the same maximum difference, **6.26217e-7**, and all convergence checks; see [current/REPORT.md](current/REPORT.md) and [python-verification.log](python-verification.log).

The comparison uses explicitly matched polarization settings (`reference`); application calculations use the literature convention (`standard`). The reference ran with a minimal ROOT adapter, not a complete ROOT/GSL installation.

## Figures and practical limits

The standalone PNG/SVG teaching figures were regenerated with the application's current default physics, independently of the comparison CSV. The PNG was visually inspected for readable labels, axes and curves.

Frontend checks use Streamlit AppTest, including actual file-uploader bytes and English/Greek interactions. Numerical and theoretical checks do not establish experimental accuracy for arbitrary measurements; stopping tables and measurement examples supplied for demonstration are synthetic.
