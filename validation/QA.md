# Verification record

Checked on **2026-11-16**, macOS ARM64 / Python 3.14. Dependency versions are pinned in `../requirements.txt`.


## Interface and result exploration update — 2026-11-16

The complete suite passed **121 tests in 81.42 seconds** ([ux-full-tests.log](ux-full-tests.log)). After the final plot-identity and presentation adjustments, the four new user-journey tests plus translation coverage passed again: **5 tests in 9.73 seconds** ([ux-final-checks.log](ux-final-checks.log)). Physics/integration modules were not modified.

New checks verify automatic navigation to Results, exact grid-point inspection, empty curve selections with exports still available, result state across English/Greek switches, persistent detector yields, stale detector settings, efficiency scaling, missing measurement uncertainties, and zero handling on logarithmic plots without modifying the numerical arrays.

The application was exercised in an isolated headless Chrome profile against a local Streamlit server. Desktop (1440 px) and mobile (390 px) layouts were visually inspected, including Greek. No horizontal page overflow was detected. Result sub-tabs and CSV/JSON download controls were checked. Mobile heading clearance and wrapping of metric labels were corrected following that inspection. Previews are saved in [the desktop screenshot](../docs/interface.png) and [the Greek mobile screenshot](../docs/interface_mobile_el.png).

This is a local browser and interaction check, not an exhaustive device/accessibility audit. Existing one-command launchers, public-data import and numerical verification remain covered by the full suite.


## Automated tests

`./start_mac.command --test` passed **117 tests with no skips** in 72 seconds, with the TCLX inputs present; see [tests.log](tests.log). In a fresh clone the three regression tests that need those inputs are skipped with an explanation (see [tclx_inputs/README.md](tclx_inputs/README.md)).

Coverage includes:

- Twelve independent solver benchmarks: Rutherford scattering, weak E1–E4 excitation, the exact two-state sudden limit, and Alder–Winther rotor amplitudes (Table 4) and populations (Table 5); in addition, the solver matches the exact Alder–Winther rotor formula to 2 × 10⁻⁵.
- Polarization for both projectile and target excitation, using the excited nucleus as prescribed by [Orce (2016), Eq. (4) and footnote 1](https://arxiv.org/abs/1510.04087). The model strength is adjustable; formula agreement is not a universal polarizability validation.
- Probability conservation, Hermitian couplings, half-integer initial spins, signed elements, target/projectile equivalence, lab Jacobians, detector integrals and stopping-depth averaging.
- Nuclear and measurement uploads, custom headers, units, uncertainties, count efficiencies, invalid-data errors and stale-result handling.
- English/Greek controls and error messages, input preservation across language changes, empty own-data modes, every example input, instructions and downloadable formats.
- Licensing and distribution: no TCLX input is shipped with the examples, and archived evidence and inputs are hash-checked.
- Public level data: the IAEA service returns levels for 22Mg, 58Ni and 152Sm that match the cited ENSDF values (checked live; the request is sent only on the button press). Parsing skips entries with uncertain energies or non-unique spins and never guesses; the tests run without network access.
- Start scripts: all three stay consistent with `run.py` (supported Python versions, arguments, CRLF line endings for the `.bat`, executable `.command`).

## Start scripts

`start_mac.command`, `start_windows.bat` and `start_linux.sh` find Python 3.12–3.14 and call `run.py`, which creates `.venv`, installs the pinned packages and starts the app. Checked on macOS:

- A clean copy without `.venv` or TCLX inputs built its environment from scratch and ran the suite through the launcher, exit code 0; the TCLX regression tests were skipped as intended.
- The app started headless through the launcher and answered its health check.
- With only the system Python 3.9 available, the script printed the install instructions and exited with code 1.

For Linux, the script was run through bash on macOS, and the Debian/Ubuntu case (Python present without `venv`) was simulated: the script names the `python3.X-venv` package to install, and `run.py` removes a half-created `.venv` and gives the same advice instead of a misleading network error.

**The Windows script has not been run on Windows, and the Linux script has not been run on Linux.**

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

## Research workbench branch

Branch: `feature/research-analysis`. Six research workflows, Greek labels, reproducible synthetic fixtures and scientific scope are documented in `docs/RESEARCH.md`.

- Full suite: **132 passed**, 124.79 s (`research-tests.log`). This includes existing excitation/reference and UI regressions.
- Follow-up after density-response quadrature and validation hardening: **19 passed**, 75.37 s (`research-final-checks.log`).
- Final workbench interaction/export and translation checks: **3 passed**, 19.35 s (`research-ui-final.log`).
- The new E4 regression exposed azimuth aliasing from low-order numerical integration; azimuth is now integrated analytically. Full-solid-angle E4 response agrees with the density trace to floating-point precision.
- The standalone synthetic sensitivity plot was generated and visually inspected. Tests exercise Streamlit with AppTest; a new browser screenshot audit was not performed for the research screens.
- Analytical limits and synthetic inference are validated. Published raw gamma datasets, mixed/magnetic transitions and full laboratory gamma geometry remain outside the validation claim.
- Additional final checks: 10 physics/translation checks passed (`research-physics-final.log`), the profile/JSON/parameter validation test passed, and the final research interaction check passed (`research-interaction-final.log`).
- The downloadable two-energy, two-parameter synthetic fit converged from multiple starts and recovered the input elements, with objective approximately 5.94e-22 (`research-synthetic-fit.json`).

## Independent research qualification evidence

See `docs/RESEARCH_QUALIFICATION.md` and `validation/research_qualification/latest.json`.

- Published 106Cd ground-state q2/q3/gamma reproduced within printed-input/output rounding.
- Separately compiled official GOSIA March-2008 code: 15 finite E2/E3 target-excitation reference points agree within 6 ppm, covering multistep/reorientation and half-integer spins. Isolated E1/E4 reference runs were nonfinite and remain explicitly unresolved, rather than passing benchmarks.
- Independent matrix-exponential rotations and 60 photon spin/multipolarity cases pass normalization, isotropy and transfer checks.
- 500 regular Gaussian external-Q pseudoexperiments: observed 68%/95% interval coverage 67.0%/95.6%, consistent with exact 99% binomial intervals. This does not qualify general nonlinear or low-count intervals.
- Full regression: **138 passed**, 132.74 s (`research_qualification/full-tests.log`). Follow-up final physics/qualification checks: **16 passed**, 31.11 s. Follow-up UI, launcher and translation checks: **11 passed**, 23.57 s.
- Fixed covariance symmetry/PSD checks for tiny and mixed-unit variances; use SVD for local fit covariance; missing decay rates produce a clear lifetime-constraint error.
- Bibliographic experimental target: 96Sr + 120Sn, Clement et al., PRC 94, 054326 (2016). Seven published peak intensities recorded with source and original errors; missing calibration/response inputs are explicit. No reproduced experimental fit is claimed.
- Cross-platform CI workflow added but not executed remotely in this session. External GOSIA source/executable remain in ignored cache, not in the repository.
- Research qualification remains incomplete for all three requested use cases. Outstanding experimental matching, nonlinear coverage and independent scientific review are recorded in the generated report.
