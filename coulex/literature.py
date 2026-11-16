"""Verification against the published semiclassical theory of Coulomb excitation.

Everything here is implemented independently of :mod:`coulex.solver`. It uses
CODATA 2018 constants, B(Eλ) values instead of GOSIA ψ/ζ coupling constants,
and the Alder–Winther orbital integrals and rotor amplitudes instead of the
GOSIA collision functions. Agreement therefore tests the solver's couplings,
Wigner–Eckart convention, orbit, phases and integration together.

Published numbers reproduced here
---------------------------------
* AW60 Table 4: complex amplitudes A_I0(π, q) for a rigid rotor, sudden limit.
* AW60 Table 5: excitation probabilities P_I(q) of a rotational band, θ = 180°, ξ = 0.
"""
from dataclasses import dataclass, field, replace
import math
import warnings
import numpy as np
from scipy.integrate import IntegrationWarning, quad
from scipy.special import eval_legendre, lpmv
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan, wigner_3j
from .model import Level, MatrixElement, Reaction

# CODATA 2018 recommended values [CODATA18].
ALPHA = 7.2973525693e-3          # fine-structure constant
HBAR_C = 197.3269804             # MeV fm
E2 = ALPHA*HBAR_C                # e²/(4πε0), MeV fm
AMU = 931.49410242               # atomic mass unit, MeV/c²

REFERENCES = {
    'AW56': 'K. Alder, A. Bohr, T. Huus, B. Mottelson, A. Winther, [Rev. Mod. Phys. 28, 432 (1956)](https://doi.org/10.1103/RevModPhys.28.432)',
    'AW60': 'K. Alder, A. Winther, "On the theory of multiple Coulomb excitation with heavy ions", '
            '[Mat. Fys. Medd. Dan. Vid. Selsk. 32, no. 8 (1960)](https://gymarkiv.sdu.dk/MFM/kdvs/mfm%2030-39/mfm-32-8.pdf)',
    'AW75': 'K. Alder, A. Winther, Electromagnetic Excitation (North-Holland, Amsterdam, 1975)',
    'BM75': 'A. Bohr, B. R. Mottelson, Nuclear Structure, Vol. II (Benjamin, Reading, 1975)',
    'R1911': 'E. Rutherford, Phil. Mag. 21, 669 (1911)',
    'CODATA18': 'E. Tiesinga, P. J. Mohr, D. B. Newell, B. N. Taylor, Rev. Mod. Phys. 93, 025010 (2021)',
    'GOSIA': 'T. Czosnyka, D. Cline, C. Y. Wu, Bull. Am. Phys. Soc. 28, 745 (1983); GOSIA manual, ch. 3',
    'ORCE16': 'J. N. Orce, [Nuclear polarization effects in Coulomb excitation studies (2016)](https://arxiv.org/abs/1510.04087), Eq. (4) and footnote 1',
}

# AW60 Table 4 (p. 33): A_I0(π, q) = Re + i Im, for I = 0, 2, 4.
AW60_TABLE4 = {
    1.0: {0: (0.83311, 0.02081), 2: (-0.04427, -0.23461), 4: (-0.04567, 0.01123)},
    2.0: {0: (0.44537, 0.12960), 2: (-0.11265, -0.31506), 4: (-0.13173, 0.06754)},
    3.0: {0: (0.06838, 0.28073), 2: (-0.09370, -0.23062), 4: (-0.16731, 0.13599)},
}
# AW60 Table 5 (p. 50): P_I(q), backward scattering, ξ = 0, ground-state spin 0.
AW60_TABLE5 = {
    1.0: {0: 0.6945, 2: 0.2850, 4: 0.0199, 6: 0.0006},
    2.0: {0: 0.2152, 2: 0.5597, 4: 0.1972, 6: 0.0260, 8: 0.0018, 10: 0.0001},
    3.0: {0: 0.0835, 2: 0.3098, 4: 0.4184, 6: 0.1572, 8: 0.0280, 10: 0.0029, 12: 0.0002},
}


def _complex_quad(function, a, b, **options):
    with warnings.catch_warnings():
        # Tails below 1e-20 trigger harmless round-off notices at these tolerances.
        warnings.simplefilter('ignore', IntegrationWarning)
        real = quad(lambda x: function(x).real, a, b, **options)[0]
        imag = quad(lambda x: function(x).imag, a, b, **options)[0]
    return complex(real, imag)


@dataclass(frozen=True)
class Orbit:
    """Symmetrized Alder–Winther orbit quantities for one transition [AW56]."""
    beta: float      # √(v_i v_f)/c
    a: float         # half the distance of closest approach in a head-on collision, fm
    xi: float        # adiabaticity parameter ξ = η_f − η_i
    z_partner: int   # charge of the nucleus that is NOT excited


def symmetrized_orbit(reaction: Reaction, excitation_energy: float) -> Orbit:
    z_exc, a_exc, z_partner, a_partner, energy = reaction.effective_nuclei
    reduced = AMU*a_exc*a_partner/(a_exc+a_partner)
    e_initial = energy*a_partner/(a_exc+a_partner)
    e_final = e_initial-excitation_energy
    if e_final <= 0:
        raise ValueError('The exit channel is closed.')
    beta_i, beta_f = math.sqrt(2*e_initial/reduced), math.sqrt(2*e_final/reduced)
    eta = lambda beta: z_exc*z_partner*ALPHA/beta
    return Orbit(math.sqrt(beta_i*beta_f), z_exc*z_partner*E2/(2*math.sqrt(e_initial*e_final)),
                 eta(beta_f)-eta(beta_i), z_partner)


def orbital_integral(lam: int, mu: int, theta: float, xi: float) -> complex:
    """I_λμ(θ, ξ) of [AW56]:

    ∫ exp[iξ(ε sinh w + w)] (cosh w + ε + i√(ε²−1) sinh w)^μ / (ε cosh w + 1)^(λ+μ) dw.

    For ξ > 0 the path is moved to Im w = π/2, where the phase factor decays as
    exp(−ξ ε cosh u). The integrand is analytic in 0 ≤ Im w ≤ π/2 (its poles
    lie at Im w = arccos(−1/ε) > π/2), so both paths give the same exact value;
    the test-suite checks this against a direct real-axis quadrature.
    """
    if not 0 < theta <= 180 or xi < 0:
        raise ValueError('Require 0 < θ ≤ 180° and ξ ≥ 0.')
    eps = 1/math.sin(math.radians(theta)/2)
    root = math.sqrt(max(0., eps*eps-1))
    shift = 1j*math.pi/2 if xi > 0 else 0.

    def integrand(u):
        w = u+shift
        numerator = np.cosh(w)+eps+1j*root*np.sinh(w)
        return np.exp(1j*xi*(eps*np.sinh(w)+w))*numerator**mu/(eps*np.cosh(w)+1)**(lam+mu)

    # |integrand| ≈ (2/ε)^λ e^(−λ|u|): stop where it is below ~1e-17.
    limit = min(60., (40.+lam*math.log(2/eps))/lam)
    return _complex_quad(integrand, -limit, limit, limit=500, epsabs=1e-15, epsrel=1e-12, points=[0.])


def _y_equator_squared(lam: int, mu: int) -> float:
    """|Y_λμ(π/2, 0)|²."""
    return ((2*lam+1)/(4*math.pi)*math.factorial(lam-abs(mu))/math.factorial(lam+abs(mu))
            * lpmv(abs(mu), lam, 0.)**2)


def first_order_probability(reaction: Reaction, theta: float, final: int) -> float:
    """First-order probability ground → `final`, summed over substates [AW56, AW75]:

    P = (Z e/ħv)² a^(−2λ) B(Eλ↑) · 16π²/(2λ+1)³ · Σ_μ |Y_λμ(π/2,0)|² |I_λμ(θ,ξ)|²,

    where Z is the partner's charge. Different λ add without interference after
    the sum over magnetic substates.
    """
    ground, level = reaction.levels[0], reaction.levels[final]
    orbit = symmetrized_orbit(reaction, level.energy-ground.energy)
    total = 0.
    for me in reaction.elements:
        if {me.initial, me.final} != {0, final} or me.value == 0 or final == 0:
            continue
        lam = me.multipolarity
        b_up = (me.value*10**lam)**2/(2*ground.spin+1)  # e² fm^(2λ)
        angular = sum(_y_equator_squared(lam, mu)*abs(orbital_integral(lam, mu, theta, orbit.xi))**2
                      for mu in range(-lam, lam+1) if (lam+mu) % 2 == 0)
        total += ((orbit.z_partner*ALPHA/orbit.beta)**2*b_up/orbit.a**(2*lam)
                  * 16*math.pi**2/(2*lam+1)**3*angular)
    return total


def strength_parameter(reaction: Reaction, final: int, lam: int, value: float) -> float:
    """Alder–Winther χ^(λ) for ground → `final` [AW56, AW75]; value in e b^(λ/2)."""
    orbit = symmetrized_orbit(reaction, reaction.levels[final].energy)
    double_factorial = math.prod(range(2*lam+1, 0, -2))
    return (math.sqrt(16*math.pi)*math.factorial(lam-1)/double_factorial
            * orbit.z_partner*(ALPHA/orbit.beta)*value*10**lam/orbit.a**lam
            / math.sqrt(2*reaction.levels[0].spin+1))


def rutherford_codata(reaction: Reaction, theta: float) -> float:
    """Elastic Rutherford cross section [R1911] with CODATA e², in barn/sr."""
    d = reaction.projectile_z*reaction.target_z*E2/reaction.energy_cm
    return (d/4)**2/math.sin(math.radians(theta)/2)**4/100


def rotor_matrix_element(spin_i: float, spin_f: float, q0: float) -> float:
    """Rigid-rotor K=0 reduced E2 element <I_i||E2||I_f> in e b; Q0 in e b [BM75]."""
    cg = float(clebsch_gordan(Rational(int(2*spin_i), 2), 2, Rational(int(2*spin_f), 2), 0, 0, 0))
    return math.sqrt(2*spin_i+1)*cg*math.sqrt(5/(16*math.pi))*q0


def rotor_q0_from_be2(be2_up: float) -> float:
    """Intrinsic quadrupole moment Q0 (e b) from B(E2; 0+ → 2+) in e² b² [BM75]."""
    return math.sqrt(16*math.pi*be2_up/5)


def spectroscopic_quadrupole(spin: float, diagonal: float) -> float:
    """Q_s(J) = √(16π/5) (J 2 J; −J 0 J) <J||E2||J>, in e b (GOSIA convention)."""
    two_j = int(round(2*spin))
    if two_j < 2:
        return 0.
    coefficient = float(wigner_3j(Rational(two_j, 2), 2, Rational(two_j, 2),
                                  -Rational(two_j, 2), 0, Rational(two_j, 2)))
    return math.sqrt(16*math.pi/5)*coefficient*diagonal


def diagonal_from_quadrupole(spin: float, q_s: float) -> float:
    """Inverse of :func:`spectroscopic_quadrupole`: <J||E2||J> from Q_s."""
    return q_s/spectroscopic_quadrupole(spin, 1.)


def aw60_amplitude(spin: int, q: float) -> complex:
    """A_I0(π, q) = exp(2iq/3) ∫₀¹ P_I(x) exp(−2iqx²) dx, AW60 Eq. (5.14) at θ = 180°."""
    return np.exp(2j*q/3)*_complex_quad(lambda x: eval_legendre(spin, x)*np.exp(-2j*q*x*x), 0, 1,
                                         limit=200, epsabs=1e-14, epsrel=1e-12)


def aw60_probabilities(q: float, spins) -> np.ndarray:
    """P_I = (2I+1)|A_I0(π, q)|² for a K=0 band with a 0+ ground state [AW60]."""
    return np.array([(2*s+1)*abs(aw60_amplitude(int(s), q))**2 for s in spins])


def aw60_q(reaction: Reaction, q0: float) -> float:
    """AW60 Eq. (5.11): q = Z e Q0 / (4 ħ v a²), with Q0 in e b, for ξ = 0."""
    orbit = symmetrized_orbit(reaction, 0.)
    return orbit.z_partner*(ALPHA/orbit.beta)*q0*100/(4*orbit.a**2)


def degenerate_rotor(reaction: Reaction, q0: float, max_spin: int) -> Reaction:
    """K=0 band 0+, 2+, … with every level at zero energy (ξ = 0); couplings from Q0."""
    spins = list(range(0, max_spin+1, 2))
    elements = []
    for i, spin in enumerate(spins):
        if spin:
            elements.append(MatrixElement(i, i, rotor_matrix_element(spin, spin, q0), 2))
        if i+1 < len(spins):
            elements.append(MatrixElement(i, i+1, rotor_matrix_element(spin, spin+2, q0), 2))
    return replace(reaction, levels=tuple(Level(float(s), 0.) for s in spins),
                   elements=tuple(elements), dipole_strength=0.)


def rotor_for_q(reaction: Reaction, q: float, max_spin: int) -> Reaction:
    """Degenerate rotor whose AW60 parameter q has the requested value."""
    return degenerate_rotor(reaction, q/aw60_q(reaction, 1.), max_spin)


# --------------------------------------------------------------------------
# Benchmark suite shown in the app and run by the tests.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Benchmark:
    group: str        # English; translated by the UI
    check: str        # English template with {placeholders}; translated by the UI
    references: str   # reference keys, e.g. 'AW56, AW75'
    expected: float
    computed: float
    tolerance: float
    relative: bool = True
    params: dict = field(default_factory=dict)

    @property
    def label(self) -> str:
        return self.check.format(**self.params)

    @property
    def difference(self) -> float:
        delta = abs(self.computed-self.expected)
        return delta/abs(self.expected) if self.relative else delta

    @property
    def passed(self) -> bool:
        return bool(self.difference <= self.tolerance)


def benchmark_suite(reaction: Reaction, settings=None, progress=None):
    """Run every literature benchmark on the kinematics of `reaction`.

    Level schemes and couplings are replaced by benchmark-specific ones; only
    the nuclei and beam energy of `reaction` are used.
    """
    from .observables import rutherford
    from .solver import CoupledChannels, SolverSettings
    settings = settings or SolverSettings(rtol=1e-11, atol=1e-15)
    base = replace(reaction, excitation='projectile', dipole_strength=0.)
    rows, steps = [], 13

    def tick():
        if progress:
            progress(min(1., (len(rows)+1)/steps))

    rows.append(Benchmark('Rutherford scattering', 'Elastic dσ/dΩ at θcm = 90° (barn/sr)', 'R1911, CODATA18',
                          rutherford_codata(base, 90.), float(rutherford(base, 90.)), 1e-4))
    weak = [(2, 2., 1, 60.), (2, 2., 1, 120.), (2, 2., 1, 180.), (1, 1., -1, 120.), (3, 3., -1, 120.),
            (4, 4., 1, 120.)]
    excitation = min(0.25*base.energy_cm, 1.0)
    for lam, spin, parity, theta in weak:
        tick()
        model = replace(base, levels=(Level(0., 0.), Level(spin, excitation, parity)),
                        elements=(MatrixElement(0, 1, 2e-4 if lam == 1 else 5e-4, lam),))
        expected = first_order_probability(model, theta, 1)
        computed = CoupledChannels(model).solve(theta, settings).probabilities[1]
        rows.append(Benchmark('First-order perturbation theory', 'E{lam} 0+ → {state}, P at θcm = {theta}°',
                              'AW56, AW75', expected, computed, 1e-4,
                              params=dict(lam=lam, state=f'{spin:g}{"+" if parity > 0 else "−"}', theta=f'{theta:g}')))
    tick()
    two = replace(base, levels=(Level(0., 0.), Level(2., 0.)), elements=(MatrixElement(0, 1, 1., 2),))
    value = 1/strength_parameter(two, 1, 2, 1.)  # χ = 1 rad
    two = replace(two, elements=(MatrixElement(0, 1, value, 2),))
    rows.append(Benchmark('Sudden limit, two states', 'P(2+) = sin²χ for χ = 1, θcm = 180°, ξ = 0', 'AW60 §4',
                          math.sin(1.)**2, CoupledChannels(two).solve(180., settings).probabilities[1], 1e-4))
    tick()
    deviation = 0.
    for q, table in AW60_TABLE4.items():
        for spin, (real, imag) in table.items():
            amplitude = aw60_amplitude(spin, q)
            deviation = max(deviation, abs(amplitude.real-real), abs(amplitude.imag-imag))
    # Table 4 prints five decimals. All entries agree to within one unit of the last digit; the q = 3
    # entry Re A00 is printed as 0.06838 while the exact value is 0.0683853.
    rows.append(Benchmark('Sudden limit, rigid rotor', 'Formula reproduces AW60 Table 4 amplitudes (max |ΔRe|, |ΔIm|)',
                          'AW60 Table 4', 0., deviation, 1e-5, relative=False))
    for q, table in AW60_TABLE5.items():
        tick()
        rotor = rotor_for_q(base, q, 22)
        computed = CoupledChannels(rotor).solve(180., settings).probabilities
        worst = max(table, key=lambda spin: abs(computed[spin//2]-table[spin]))
        rows.append(Benchmark('Sudden limit, rigid rotor', 'q = {q}: P_I (I = 0…{top}), largest deviation at I = {worst}',
                              'AW60 Table 5', table[worst], float(computed[worst//2]), 1e-4, relative=False,
                              params=dict(q=f'{q:g}', top=max(table), worst=worst)))
    if progress:
        progress(1.)
    return rows
