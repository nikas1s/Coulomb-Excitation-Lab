"""Full magnetic-substate coupled channels, integrated with SciPy DOP853.

Physics conventions follow the semiclassical coupled-channel formalism. No Numerical Recipes routines are used.
The collision functions and the integration of the amplitudes over the orbit parameter ω are a Python adaptation of
TCLX and its successor Cygnus by J. Henderson (https://github.com/jhenderson88/Cygnus, src/PointCoulEx.cxx; GNU GPL v3),
which follow the GOSIA formalism. This file is distributed under the GNU GPL v3; see LICENSE.
No probability clipping or renormalization is performed.
"""

from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import csr_matrix
from sympy import Rational
from sympy.physics.wigner import wigner_3j
from .model import Reaction


@lru_cache(maxsize=100000)
def three_j(j1, j2, j3, m1, m2, m3):
    """Arguments are twice the angular momenta; evaluate exactly before rounding."""
    return float(wigner_3j(*(Rational(int(x), 2) for x in (j1, j2, j3, m1, m2, m3))))


def collision_functions(lam, epsilon, omega, polarization=0.0):
    """Q[Eλ, |μ|] in the orbit frame; odd μ components are imaginary."""
    a = math.cosh(omega) + epsilon
    b = epsilon * math.cosh(omega) + 1
    c = math.sqrt(max(0.0, epsilon**2 - 1)) * math.sinh(omega)
    if lam == 1:
        values = [a/2, -1j*c/(2*math.sqrt(2))]
    elif lam == 2:
        values = [3/4*(2*a*a-c*c), -1j*3*math.sqrt(3/2)*a*c/2,
                  -3*math.sqrt(3/2)*c*c/4]
    elif lam == 3:
        values = [15/8*a*(2*a*a-3*c*c), -1j*15*math.sqrt(3)/16*c*(4*a*a-c*c),
                  -15*math.sqrt(15/2)/8*a*c*c, 1j*15*math.sqrt(5)/16*c**3]
    elif lam == 4:
        # The E4 coefficient requires real division.
        values = [35/32*(8*a**4-24*a*a*c*c+3*c**4),
                  -1j*35*math.sqrt(5)/16*a*c*(4*a*a-3*c*c),
                  -35*math.sqrt(5/2)/16*c*c*(6*a*a-c*c),
                  1j*35*math.sqrt(35)/16*a*c**3, 35*math.sqrt(35/2)/32*c**4]
    else:
        raise ValueError("Collision functions are implemented for electric E1–E4 only.")
    q = np.asarray(values, dtype=complex) / b**(2*lam)
    return q * (1 - polarization/b) if lam == 2 else q


@dataclass(frozen=True)
class SolverSettings:
    rtol: float = 1e-9
    atol: float = 1e-12
    tail_accuracy: float = 1e-8
    extra_omega: float = 0.0
    max_step: float = 0.08
    method: str = "DOP853"

    def __post_init__(self):
        if not 1e-13 <= self.rtol <= 1e-3 or not 1e-15 <= self.atol <= 1e-5:
            raise ValueError("ODE tolerances are outside the supported range.")
        if not 1e-14 <= self.tail_accuracy <= 1e-4:
            raise ValueError("Tail parameter must be between 1e-14 and 1e-4.")
        if not math.isfinite(self.extra_omega) or not 0 <= self.extra_omega <= 4:
            raise ValueError("Extra orbit range must be between 0 and 4.")
        if not math.isfinite(self.max_step) or not 0 < self.max_step <= 0.5:
            raise ValueError("Maximum orbit step must lie in (0, 0.5].")
        if self.method not in ("DOP853", "RK45"):
            raise ValueError("Choose DOP853 or RK45.")


@dataclass
class AngleResult:
    angle: float
    probabilities: np.ndarray
    substate_probabilities: np.ndarray
    omega: np.ndarray
    history: np.ndarray
    norm_error: float
    evaluations: int
    endpoint: float


class CoupledChannels:
    def __init__(self, reaction: Reaction):
        self.reaction = reaction
        self.level_index = np.repeat(np.arange(len(reaction.levels)),
                                     [int(2*x.spin+1) for x in reaction.levels])
        self.m = np.concatenate([np.arange(-x.spin, x.spin+1) for x in reaction.levels])
        self.size = len(self.m)
        self.ground_size = int(2*reaction.levels[0].spin+1)
        zp, ap, zt, at, energy = reaction.effective_nuclei
        remaining = energy - (1 + ap/at)*np.array([x.energy for x in reaction.levels])
        self.eta = 0.007297352*zp*zt/(0.046337*np.sqrt(remaining/ap))
        self.eta_sub = self.eta[self.level_index] - self.eta[0]
        constants = {1: 5.169286, 2: 14.359366, 3: 56.982577, 4: 263.812653}
        # Store independent sparse operators per λ, |μ|. Hermitian reduced-ME
        # symmetry handles odd spin differences without relying on a J=0 shortcut.
        entries = {}
        for me in reaction.elements:
            if me.value == 0:
                continue
            lam = me.multipolarity
            pairs = [(me.initial, me.final, me.value)]
            if me.initial != me.final:
                phase = (-1)**int(reaction.levels[me.initial].spin-reaction.levels[me.final].spin)
                pairs.append((me.final, me.initial, phase*me.value))
            for source, dest, value in pairs:
                ji, jf = reaction.levels[source].spin, reaction.levels[dest].spin
                psi = (constants[lam]*zt*math.sqrt(ap)/(zp*zt*(1+ap/at))**lam
                       * (remaining[source]*remaining[dest])**((2*lam-1)/4)*value)
                for row in np.flatnonzero(self.level_index == dest):
                    for col in np.flatnonzero(self.level_index == source):
                        mi, mf = self.m[col], self.m[row]
                        mu = int(round(mi-mf))
                        if abs(mu) > lam:
                            continue
                        zeta = ((-1)**int(round(ji-mi))*math.sqrt(2*lam+1)*psi
                                * three_j(round(2*ji), 2*lam, round(2*jf),
                                          round(-2*mi), 2*mu, round(2*mf)))
                        if zeta:
                            rows, cols, values = entries.setdefault((lam, abs(mu)), ([], [], []))
                            rows.append(row); cols.append(col); values.append(zeta)
        self.operators = {key: csr_matrix((v, (r, c)), shape=(self.size, self.size))
                          for key, (r, c, v) in entries.items()}
        self.lambdas = sorted({lam for lam, _ in self.operators})

    def hamiltonian(self, omega, epsilon):
        """Dense interaction-picture matrix, useful for inspection and diagnostics."""
        h = np.zeros((self.size, self.size), complex)
        for (lam, mu), matrix in self.operators.items():
            h += collision_functions(lam, epsilon, omega, self.reaction.polarization)[mu]*matrix.toarray()
        phase = np.exp(1j*self.eta_sub*(epsilon*math.sinh(omega)+omega))
        return phase[:, None]*h*phase.conj()[None, :]

    def solve(self, angle: float, settings: SolverSettings | None = None, history_points=0):
        settings = settings or SolverSettings()
        if not math.isfinite(angle) or not 0 < angle <= 180:
            raise ValueError("Center-of-mass angle must lie in (0, 180].")
        epsilon = 1/math.sin(math.radians(angle)/2)
        # Finite-orbit range heuristic; integrate exactly to both endpoints.
        # The parameter is a tail-range heuristic, NOT a certified error bound.
        endpoint = max(2.0, math.log(1/(epsilon*math.sqrt(settings.tail_accuracy)))) + settings.extra_omega
        y0 = np.zeros((self.size, self.ground_size), complex)
        y0[:self.ground_size] = np.eye(self.ground_size)

        def derivative(omega, flat):
            amplitude = flat.reshape(self.size, self.ground_size)
            phase = np.exp(1j*self.eta_sub*(epsilon*math.sinh(omega)+omega))
            rotated = phase.conj()[:, None]*amplitude
            result = np.zeros_like(amplitude)
            q = {lam: collision_functions(lam, epsilon, omega, self.reaction.polarization)
                 for lam in self.lambdas}
            for (lam, mu), operator in self.operators.items():
                result += q[lam][mu]*(operator @ rotated)
            return (-1j*phase[:, None]*result).ravel()

        solution = solve_ivp(derivative, (-endpoint, endpoint), y0.ravel(), method=settings.method,
                             rtol=settings.rtol, atol=settings.atol, max_step=settings.max_step,
                             dense_output=bool(history_points))
        if not solution.success:
            raise RuntimeError(f"ODE solver failed at {angle}°: {solution.message}")
        amplitudes = solution.y.reshape(self.size, self.ground_size, -1)
        norms = np.sum(abs(amplitudes)**2, axis=0)
        norm_error = float(np.max(abs(norms-1)))
        if not np.isfinite(norm_error) or norm_error > max(1e-6, 100*settings.rtol):
            raise RuntimeError(f"Probability conservation failed ({norm_error:.3g}); tighten tolerances.")
        substate = np.mean(abs(amplitudes[:, :, -1])**2, axis=1)
        probabilities = np.bincount(self.level_index, weights=substate, minlength=len(self.reaction.levels))
        omega = np.linspace(-endpoint, endpoint, history_points) if history_points else np.array([])
        history = np.empty((len(self.reaction.levels), len(omega)))
        if history_points:
            populations = np.mean(abs(solution.sol(omega).reshape(self.size, self.ground_size, -1))**2, axis=1)
            for level in range(len(self.reaction.levels)):
                history[level] = populations[self.level_index == level].sum(axis=0)
        return AngleResult(float(angle), probabilities, substate, omega, history,
                           norm_error, solution.nfev, endpoint)

    def scan(self, angles, settings=None, progress=None):
        results = []
        for i, angle in enumerate(angles):
            results.append(self.solve(float(angle), settings))
            if progress:
                progress((i+1)/len(angles))
        return results
