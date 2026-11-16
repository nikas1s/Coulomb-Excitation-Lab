# Numerical dependencies and source provenance

The runtime solver contains no Numerical Recipes source or a translation of its routines. It uses the public numerical APIs of these open-source projects:

| Dependency | Use | Upstream license |
|---|---|---|
| NumPy | Arrays, elementary math, Gauss–Legendre nodes | BSD-3-Clause |
| SciPy | DOP853/RK45, sparse operators, quadrature and PCHIP | BSD-3-Clause, with bundled third-party notices |
| SymPy | Exact Wigner 3j values | BSD-3-Clause |
| pandas | Tables and CSV export | BSD-3-Clause |
| Streamlit | Local application frontend | Apache-2.0 |
| Plotly.py | Interactive scientific figures | MIT |
| Matplotlib | Standalone validation and teaching plots | Matplotlib/PSF-based license |
| pytest | Automated tests | MIT |

All of these licences are compatible with distributing this project under the GNU GPL v3. Exact direct and transitive versions are pinned in `requirements.txt`. The installed distributions carry their own full licenses and bundled third-party notices; those remain authoritative. [SciPy's license statement](https://scipy.org/about/) and [SymPy's license](https://github.com/sympy/sympy/blob/master/LICENSE) document their open-source status. This inventory is not a blanket legal or patent opinion.

## Origin and licence

This project is a modified Python adaptation of [TCLX](https://github.com/jhenderson88/TCLX) and its successor [Cygnus](https://github.com/jhenderson88/Cygnus) by J. Henderson, acknowledging the earlier CLX work of H. Ower and J. Gerl. The collision functions and the integration of the excitation amplitudes follow that code, which Cygnus publishes under the GNU GPL v3; this project is therefore distributed under the GNU GPL v3 (see `LICENSE` and the License section of `README.md`).

TCLX itself carries no licence. Its source, source snapshots, the ROOT adapter and the compiled reference executable have been removed, and its two example input files are not distributed (see `validation/tclx_inputs/README.md` to obtain them). Only cited comparison data (the probabilities and cross sections in `validation/results/comparison.csv`) and reports are retained; the full text printed by TCLX is not distributed. All built-in examples were written for this project from the cited literature.

### Provenance by component

Component-level comparison of TCLX and Cygnus (function names and roles, checked 2026-11-16). Every Python component that corresponds to TCLX functionality has a counterpart in GPL-3.0 Cygnus:

| Python module | TCLX (no licence) | Cygnus counterpart (GPL-3.0) |
|---|---|---|
| `coulex/solver.py`: collision functions, coupling matrices, amplitude integration over ω | `TCLX`: `ComputeAmpDerivativeMatrices`, `Integration`, `MakeMagneticSubstates` | `PointCoulEx`: `CollisionFunction`, `ComputeAmpDerivativeMatrices`, `Integration` |
| `coulex/model.py`: dipole polarization | `TCLX`: `ElectricDipoleNormalization` | `PointCoulEx`: `ElectricDipoleNormalization` |
| `coulex/model.py`, `observables.py`: kinematics, Rutherford, CM/lab conversion | `TReactions`: `ClosestApproach`, `EtaCalc`, `RelativeVelocity`, `EvalRutherford` | `Reaction`: `ClosestApproach`, `EtaCalc`, `RelativeVelocity`, `Rutherford`, `ConvertThetaCmToLab` |
| `coulex/stopping.py`, `workflow.py`: energy loss in the target | `TExperiment`: `SetupEnergyLoss`, `PerformCalculationWithELoss` | `StoppingPower`, `ExperimentRange`: `SetStopping`, `IntegrateThetaEnergy` |
| `coulex/observables.py`: detector integrals and yields | `TExperiment`: `IntegrateTheta`, `PlotYieldLab` | `ExperimentRange`: `IntegrateRange`, `SetDetectorEff` |

The only TCLX-specific element is the reaction text layout, which `coulex/model.py` reads with newly written code (an input format, not copied code). TCLX's detector-specific code (TIGRESS, BAMBINO, SPICE) was not adapted. Measurement comparisons, uploads, the interface, translations, literature benchmarks and examples are new.

Physics expressions, conventions and numerical constants are traced in `docs/NUMERICS.md`. Verification runs entirely in Python against saved numerical outputs.
