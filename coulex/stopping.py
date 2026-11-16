"""Energy loss using an explicitly supplied, positive stopping-power table.

No proprietary coefficient tables are embedded. Integration refuses extrapolation.
"""

from dataclasses import dataclass
from io import StringIO
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator


@dataclass
class StoppingTable:
    energy: np.ndarray
    stopping: np.ndarray

    def __post_init__(self):
        self.energy = np.asarray(self.energy, float)
        self.stopping = np.asarray(self.stopping, float)
        if (self.energy.ndim != 1 or len(self.energy) < 2 or self.energy.shape != self.stopping.shape
                or np.any(~np.isfinite(self.energy)) or np.any(~np.isfinite(self.stopping))
                or np.any(self.energy <= 0) or np.any(self.stopping <= 0) or np.any(np.diff(self.energy) <= 0)):
            raise ValueError("Stopping table needs increasing positive energies and positive finite stopping powers.")
        self.interpolate = PchipInterpolator(self.energy, self.stopping, extrapolate=False)

    @classmethod
    def from_csv(cls, text):
        data = np.genfromtxt(StringIO(text), delimiter=",", names=True)
        if data.dtype.names != ("energy_mev", "stopping_mev_per_mg_cm2"):
            raise ValueError("CSV columns must be energy_mev,stopping_mev_per_mg_cm2.")
        return cls(np.atleast_1d(data["energy_mev"]), np.atleast_1d(data["stopping_mev_per_mg_cm2"]))

    def _trajectory(self, incident_energy, thickness):
        if not np.isfinite(thickness) or thickness < 0:
            raise ValueError("Thickness must be finite and nonnegative.")
        if not self.energy[0] < incident_energy <= self.energy[-1]:
            raise ValueError("Incident energy must lie inside the stopping table, above its minimum.")
        if thickness == 0:
            return lambda depth: np.full_like(np.asarray(depth, float), incident_energy)

        def derivative(x, energy):
            # Clipping only permits the solver's trial stages across the terminal
            # event; no accepted profile outside the measured table is returned.
            return -self.interpolate(np.clip(energy, self.energy[0], self.energy[-1]))

        def below_table(x, energy):
            return energy[0]-self.energy[0]

        below_table.terminal = True
        below_table.direction = -1
        sol = solve_ivp(derivative, (0, thickness), [incident_energy], method="DOP853",
                        rtol=1e-10, atol=1e-12, events=below_table, dense_output=True)
        if not sol.success or sol.t[-1] < thickness:
            raise ValueError("Beam exits the stopping-table range inside the target; supply a wider table.")
        return lambda depth: sol.sol(depth)[0]

    def profile(self, incident_energy, thickness, points=101):
        trajectory = self._trajectory(incident_energy, thickness)
        depth = np.linspace(0, thickness, points)
        return depth, trajectory(depth)

    def quadrature(self, incident_energy, thickness, order=6):
        """Depth nodes and normalized Gauss–Legendre weights for thick-target averages."""
        trajectory = self._trajectory(incident_energy, thickness)
        nodes, weights = np.polynomial.legendre.leggauss(order)
        sample_depth = (nodes+1)*thickness/2
        return sample_depth, trajectory(sample_depth), weights/2
