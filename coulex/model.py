"""Validated reaction inputs. Energies in MeV; reduced Eλ elements in e b^(λ/2)."""

from dataclasses import dataclass, replace
import math
import numpy as np


@dataclass(frozen=True)
class Level:
    spin: float
    energy: float
    parity: int = 1
    k: float = 0.0


@dataclass(frozen=True)
class MatrixElement:
    initial: int  # Zero-based level indices, in file order.
    final: int
    value: float  # <initial || Eλ || final>, real-valued reduced element.
    multipolarity: int = 2


@dataclass(frozen=True)
class Reaction:
    title: str
    projectile_z: int
    projectile_a: int
    target_z: int
    target_a: int
    energy_lab: float
    levels: tuple[Level, ...]
    elements: tuple[MatrixElement, ...]
    theta_min: float = 1.0
    theta_max: float = 180.0
    theta_step: float = 1.0
    excitation: str = "projectile"
    dipole_strength: float = 0.005
    polarization_convention: str = "standard"

    def __post_init__(self):
        for name in ("projectile_z", "projectile_a", "target_z", "target_a"):
            value = getattr(self, name)
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        if self.projectile_z > self.projectile_a or self.target_z > self.target_a:
            raise ValueError("A nuclear charge Z cannot exceed its mass number A.")
        if not math.isfinite(self.energy_lab) or self.energy_lab <= 0:
            raise ValueError("Beam energy must be finite and positive (total MeV, not MeV/u).")
        if self.excitation not in ("projectile", "target"):
            raise ValueError("Excitation must be 'projectile' or 'target'.")
        if not math.isfinite(self.dipole_strength) or self.dipole_strength < 0:
            raise ValueError("Dipole strength must be finite and nonnegative.")
        if self.polarization_convention not in ("standard", "reference"):
            raise ValueError("Unknown polarization convention.")
        if not self.levels or self.levels[0].energy != 0:
            raise ValueError("The first level must be the ground state at 0 MeV.")
        for level in self.levels:
            if not all(math.isfinite(x) for x in (level.spin, level.energy, level.k)):
                raise ValueError("Level data must be finite.")
            if level.spin < 0 or not float(2 * level.spin).is_integer():
                raise ValueError("Spins must be nonnegative integers or half-integers.")
            if level.parity not in (-1, 1):
                raise ValueError("Parity must be +1 or -1.")
            if not 0 <= level.energy < self.energy_cm:
                raise ValueError("Every level must lie below the available center-of-mass energy.")
            if (level.spin - self.levels[0].spin) % 1 != 0:
                raise ValueError("All levels must have the same integer/half-integer spin character.")
        seen = set()
        for me in self.elements:
            if not 0 <= me.initial < len(self.levels) or not 0 <= me.final < len(self.levels):
                raise ValueError("A matrix element refers to a nonexistent level.")
            if me.multipolarity not in (1, 2, 3, 4):
                raise ValueError("Only electric E1–E4 transitions are supported; magnetic codes are rejected.")
            if not math.isfinite(me.value):
                raise ValueError("Matrix elements must be finite.")
            key = (min(me.initial, me.final), max(me.initial, me.final), me.multipolarity)
            if key in seen:
                raise ValueError("Duplicate matrix element (including a reversed duplicate).")
            seen.add(key)
            a, b = self.levels[me.initial], self.levels[me.final]
            if me.value and not abs(a.spin - b.spin) <= me.multipolarity <= a.spin + b.spin:
                raise ValueError("A nonzero matrix element violates the angular-momentum triangle rule.")
            if me.value and a.parity * b.parity != (-1) ** me.multipolarity:
                raise ValueError("A nonzero electric matrix element violates parity selection.")
        angle_grid(self.theta_min, self.theta_max, self.theta_step)

    @property
    def energy_cm(self):
        return self.energy_lab / (1 + self.projectile_a / self.target_a)

    @property
    def effective_nuclei(self):
        """Excited nucleus first. Swapping masses AND energy preserves relative motion."""
        if self.excitation == "projectile":
            return self.projectile_z, self.projectile_a, self.target_z, self.target_a, self.energy_lab
        return (self.target_z, self.target_a, self.projectile_z, self.projectile_a,
                self.energy_lab * self.target_a / self.projectile_a)

    @property
    def polarization(self):
        """E2 polarization coefficient; Orce (2016), Eq. (4) and footnote 1.

        The mass and charge belong to the excited nucleus. The reference
        convention is used only to reproduce the stored TCLX comparison.
        """
        zp, ap, _, at, energy = self.effective_nuclei
        if self.polarization_convention == "reference":
            return self.dipole_strength * energy * at / (zp**2 * (1 + ap / at))
        return self.dipole_strength * self.energy_cm * ap / zp**2

    @property
    def head_on_distance(self):
        # Coulomb constant in MeV fm; output in fm.
        return 1.43998 * self.projectile_z * self.target_z / self.energy_cm

    def at_energy(self, energy):
        return replace(self, energy_lab=float(energy))


def angle_grid(start, stop, step):
    if not all(math.isfinite(x) for x in (start, stop, step)):
        raise ValueError("Angle controls must be finite.")
    if not 0 < start <= stop <= 180 or step <= 0:
        raise ValueError("Require 0 < minimum ≤ maximum ≤ 180°, and a positive step.")
    if (stop - start) / step > 10000:
        raise ValueError("Use at most 10,001 angles per calculation.")
    grid = start + step * np.arange(int(math.floor((stop - start) / step + 1e-10)) + 1)
    grid = grid[grid <= stop + 1e-10]
    if not np.isclose(grid[-1], stop, rtol=0, atol=1e-10):
        grid = np.append(grid, stop)
    grid[-1] = stop
    return grid


def parse_input(text: str) -> Reaction:
    """Read the supplied text format; comments may start with // or #."""
    lines = [line.split("//", 1)[0].split("#", 1)[0].strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    try:
        n = int(lines[1])
        if n <= 0 or len(lines) < 6 + n:
            raise ValueError("The declared level count does not match the input.")
        zp, ap = map(int, lines[2].split())
        zt, at = map(int, lines[3].split())
        energy = float(lines[4])
        start, stop, step = map(float, lines[5].split())
        if stop == 0:
            stop = start
        if step == 0:
            step = stop - start if stop > start else 1.0
        levels = []
        for index, line in enumerate(lines[6:6+n], 1):
            identifier, spin, e, parity, k = line.split()
            if int(identifier) != index:
                raise ValueError("Level indices must be consecutive, starting at 1.")
            levels.append(Level(float(spin), float(e), int(parity), float(k)))
        elements = []
        for line in lines[6+n:]:
            a, b, value, lam = line.split()
            elements.append(MatrixElement(int(a)-1, int(b)-1, float(value), int(lam)))
        return Reaction(lines[0], zp, ap, zt, at, energy, tuple(levels), tuple(elements), start, stop, step)
    except (IndexError, TypeError) as error:
        raise ValueError("Incomplete reaction input; see the File formats tab for the line-by-line layout.") from error
    except ValueError as error:
        raise ValueError(f"Invalid reaction input: {error}") from error
