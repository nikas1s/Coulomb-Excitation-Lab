# Equations, conventions and numerical error

## Coordinates and units

The model input specifies projectile `(Zp, Ap)`, target `(Zt, At)`, total projectile kinetic energy `Elab` in MeV, and levels `(Jn, En, parity)`. Mass numbers approximate nuclear masses. The center-of-mass energy is

```text
Ecm = Elab / (1 + Ap/At).
```

The calculation uses rounded constants `alpha = 0.007297352`, `beta = 0.046337 sqrt(E/Ap)` and `e² = 1.43998 MeV fm`. Their finite precision is separate from integration tolerance; independent literature benchmarks use CODATA 2018 constants.

For CM deflection θ, the Rutherford orbit uses

```text
epsilon = 1 / sin(theta/2)
d0 = 1.43998 Zp Zt / Ecm      [fm, head-on distance]
a0 = d0/2
z = a0 (cosh(omega) + epsilon)
y = a0 sqrt(epsilon² − 1) sinh(omega)
r = a0 (epsilon cosh(omega) + 1)
```

This orbit frame places the trajectory in the yz plane, with closest approach at ω=0. The collision functions in `solver.py` are the electric multipole polynomials in these coordinates, with their common radial factors. The E4 leading coefficient is **35/32**, using real division. Negative and positive μ use `Q[|μ|]`; the angular coefficient supplies the corresponding phase. The app's driving-field figure shows E2, as a teaching example.

## Angular coupling and amplitudes

A nuclear level becomes `2J+1` basis states `(n,m)`, with `m = −J, −J+1, …, J`. We retain the complete basis. For an unpolarized initial nucleus, one independent amplitude column starts in each ground-state substate. This explicitly represents the initial density matrix `I/(2J0+1)`.

For source level i and destination f, define

```text
s = 1 + Ap/At
Ki = Elab − s Ei
eta_i = alpha Zp Zt / [0.046337 sqrt(Ki/Ap)]
psi_fi(λ) = Cλ Zt sqrt(Ap) (Kf Ki)^((2λ−1)/4)
             × <i || Eλ || f> / [Zp Zt s]^λ
Cλ = [5.169286, 14.359366, 56.982577, 263.812653] for E1…E4
zeta_fi = (−1)^(Ji−mi) sqrt(2λ+1) psi_fi
           × Wigner3j(Ji, λ, Jf; −mi, mi−mf, mf)
```

The reduced electric matrix elements are real. Their reverse is `(−1)^(Ji−Jf)` times the forward value. Diagonal elements are allowed when the selection rules permit them; they describe reorientation rather than excitation to a new nuclear level. SymPy evaluates the angular coefficient exactly before conversion to a Python double. Caching avoids repeated symbolic work.

The complex interaction-picture evolution is

```text
da_f/domega = −i sum_i,λ zeta_fi Qλ,|mi−mf|(epsilon,omega)
                × exp[i (eta_f−eta_i) (epsilon sinh(omega)+omega)] a_i.
```

The implementation factors the exponential into source and destination phases, then applies sparse operators per `(λ,|μ|)`. This is algebraically the same equation, with fewer repeated exponentials. Its Hamiltonian is Hermitian for valid inputs. Tests check this for all supported multipoles and half-integer spins.

Final probabilities sum squared amplitudes over final magnetic substates and average over initial columns. **No clipping or probability renormalization** hides norm drift. The solver monitors each initially occupied column at every accepted integration step and fails when drift exceeds its diagnostic threshold.

The electric dipole-polarization approximation modifies the E2 interaction:

```text
D = d Ecm A_excited / Z_excited²
d = 0.005 MeV⁻¹ (adjustable model parameter)
Q_E2 -> Q_E2 × [1 − D/(epsilon cosh(omega)+1)].
```

Here A and Z belong to the **excited nucleus**, whether projectile or target. This is the mass convention in [Orce (2016), Eq. (4) and footnote 1](https://arxiv.org/abs/1510.04087). That paper discusses alternative polarization strengths; the default is not a universal measured polarizability. The UI permits changing d or disabling the correction. When modeling explicit high-lying E1 strength, consider whether an additional effective polarization term would double-count its effect.

For target excitation the effective excited and perturbing nuclei are swapped and `Elab_effective = Elab At/Ap`, preserving relative kinematics. Formula tests cover both excitation choices and equivalence under swapping the collision partners.

## Integration and convergence

The production integration uses SciPy's public `solve_ivp` with `method="DOP853"`. Default local controls are relative tolerance `1e-9` and absolute tolerance `1e-12` on the complex amplitudes, with maximum ω step 0.08. The equations and integration endpoints are independent of the plotting sample count.

The default finite orbit endpoint is

```text
W = max(2, log[1/(epsilon sqrt(1e-8))]) + extra_omega.
```

The lower bound avoids a negative range at extremely forward angles. Integration ends exactly at ±W. The `1e-8` value is a **range heuristic**, not a certified truncation-error bound. The true initial/final orbit is infinite. E1 has a slower tail than E2, so extra range checks are particularly important for E1 or unusual inputs.

Four different errors must be examined:

1. **ODE discretization:** decrease both tolerances and the maximum step; compare with RK45, which has different coefficients and order.
2. **Finite orbit:** increase W while retaining the same ODE tolerances. Probability conservation alone cannot detect this error.
3. **Angular quadrature:** halve the angle step before integrating detector acceptance. Interpolation through a coarse grid cannot recover unresolved angular structure.
4. **Target-depth quadrature:** increase the Gauss–Legendre order when energy loss is enabled. The stopping table itself has external uncertainty.

Neither local tolerances nor this limited convergence study prove a bound for all inputs. When populations approach the absolute numerical floor, relative errors may be large. Expand the nuclear level scheme to test model-space truncation; numerical convergence within a fixed scheme does not establish its completeness.

## Cross sections and laboratory angles

The **level-dependent** Rutherford factor is expressed in barn/sr:

```text
R_n(theta) = 0.000625 d0² csc(theta/2)^4 / sqrt(1−En/Ecm)
dsigma_n/dOmega_cm = P_n R_n.
```

For zero excitation, `0.000625 = 1/(16×100)` combines the geometric factor and `100 fm² = 1 barn`.

The nonrelativistic scattered-projectile lab angle, including the exit-channel speed, is

```text
tau_n = (Ap/At) / sqrt(1−En/Ecm)
phi = atan2(sin(theta), cos(theta)+tau_n)
dOmega_cm/dOmega_lab = (1+tau_n²+2 tau_n cos(theta))^(3/2)
                       / abs(1+tau_n cos(theta)).
```

For inverse kinematics the map folds. A single lab angle can receive two CM branches. Lab plots retain the CM ordering and show each branch contribution; they do not pretend to be the branch-summed observable. The Jacobian diverges at the turning point, so detector integrals are evaluated in CM solid angle after analytically determining every accepted CM interval. No extrapolation beyond the computed grid is allowed.

`integrate_detector` uses shape-preserving cubic interpolation of the actual calculated cross sections and integrates `2π sin(theta) dtheta`, including endpoint interpolation and azimuth fraction. The interpolation does not alter the reported point probabilities. Tests compare an elastic annular integral with its closed-form Rutherford result and verify both inverse-kinematics branches for an isotropic distribution.

## Target averaging and yields

A supplied stopping table defines `S(E)` in MeV/(mg/cm²). We integrate `dE/dx = −S(E)` using DOP853 and stop if the energy leaves the table domain. Every depth quadrature node gets a new validated reaction, a full coupled-channel calculation, and its own Rutherford factor and lab acceptance. The weighted average is over uniform areal depth, not uniform energy. The beam is assumed not significantly attenuated by reactions.

For an areal density t in mg/cm²,

```text
Ntarget = t × 1e−3 × 6.02214076e23 / At     [atoms/cm²]
Ndetected = sigma[barn] × 1e−24 × Ntarget × I[1/s] × time[s] × efficiency.
```

The optional direct gamma count multiplies one populated level's detected count by a supplied gamma branching fraction and absolute gamma efficiency. Excitation matrix elements alone do not provide a complete decay scheme.

## References

The [GOSIA manual](https://www.pas.rochester.edu/~cline/Gosia/Gosia_Manual_20110730.pdf), chapter 3, describes the underlying orbit and coupled-channel framework. Numerical software interfaces are documented by [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) and [SymPy](https://docs.sympy.org/latest/modules/physics/wigner.html). No Numerical Recipes code is used.
