"""Shared calculation workflow for the UI and scripts."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from .solver import CoupledChannels, SolverSettings
from .observables import cross_sections


@dataclass
class Scan:
    angles: np.ndarray
    probabilities: np.ndarray
    cross_sections: np.ndarray
    norm_errors: np.ndarray
    energies: np.ndarray
    weights: np.ndarray
    # Keep each depth for correct state-dependent lab acceptance and yields.
    depth_cross_sections: np.ndarray


def calculate(reaction, angles, settings=None, stopping=None, thickness=0.0, order=6, progress=None):
    settings = settings or SolverSettings()
    angles = np.asarray(angles, float)
    if stopping is None:
        energies, weights = np.array([reaction.energy_lab]), np.array([1.0])
    else:
        _, energies, weights = stopping.quadrature(reaction.energy_lab, thickness, order)
    probabilities, sections, errors = [], [], []
    for i, energy in enumerate(energies):
        local = reaction.at_energy(energy)
        solver = CoupledChannels(local)
        callback = (lambda p, i=i: progress((i+p)/len(energies))) if progress else None
        results = solver.scan(angles, settings, callback)
        p = np.array([r.probabilities for r in results])
        probabilities.append(p)
        sections.append(cross_sections(local, angles, p))
        errors.append([r.norm_error for r in results])
    return Scan(angles, np.einsum("d,dal->al", weights, probabilities),
                np.einsum("d,dal->al", weights, sections), np.max(errors, axis=0),
                energies, weights, np.asarray(sections))


def results_frame(reaction, scan):
    rows = []
    for i, theta in enumerate(scan.angles):
        for level, state in enumerate(reaction.levels):
            rows.append({"theta_cm_deg": theta, "level": level+1, "spin": state.spin,
                         "energy_mev": state.energy,
                         "probability": scan.probabilities[i, level],
                         "dsigma_cm_barn_per_sr": scan.cross_sections[i, level],
                         "max_norm_error": scan.norm_errors[i]})
    return pd.DataFrame(rows)
