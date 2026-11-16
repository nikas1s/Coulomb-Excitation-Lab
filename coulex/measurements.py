"""Explicitly normalized comparisons with measured observables; no fitting."""
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from .imports import numeric_columns, integer_column
from .model import angle_grid
from .observables import (cross_sections, detector_cm_intervals, integrate_detector,
                          lab_angle, lab_jacobian, particle_yield)
from .solver import CoupledChannels, SolverSettings

SCHEMAS = {
    'cross_section': ('angle_deg','level','value'),
    'probability': ('angle_deg','level','value'),
    'particle_counts': ('angle_min_deg','angle_max_deg','level','value','efficiency'),
    'gamma_counts': ('angle_min_deg','angle_max_deg','level','value','efficiency','branching_fraction','gamma_efficiency'),
}


@dataclass(frozen=True)
class Exposure:
    beam_per_second: float = 1e5
    days: float = 5.
    thickness: float = 2.
    azimuth_fraction: float = 1.

    def __post_init__(self):
        if not all(math.isfinite(x) and x > 0 for x in (self.beam_per_second,self.days)):
            raise ValueError('Beam rate and live duration must be positive and finite.')
        if not math.isfinite(self.thickness) or self.thickness < 0:
            raise ValueError('Target thickness must be finite and nonnegative.')
        if not math.isfinite(self.azimuth_fraction) or not 0 < self.azimuth_fraction <= 1:
            raise ValueError('Azimuth coverage must lie in (0, 1].')


def validate_measurements(frame, kind, level_count, units='barn/sr'):
    if kind not in SCHEMAS:
        raise ValueError('Unknown observable.')
    data = numeric_columns(frame, SCHEMAS[kind], ('uncertainty',))
    if data.empty:
        raise ValueError('The measurement table has no observations.')
    integer_column(data,'level',1,level_count)
    if (data.value < 0).any():
        raise ValueError('Measured values must be nonnegative; background-subtracted negative observations need a separate statistical model.')
    if ((data.uncertainty <= 0) & data.uncertainty.notna()).any():
        raise ValueError('Uncertainty must be a positive one-sigma standard uncertainty, or blank if unknown.')
    if kind in ('cross_section','probability'):
        if ((data.angle_deg <= 0) | (data.angle_deg > 180)).any():
            raise ValueError('Point angles must lie in (0, 180] degrees.')
    else:
        if ((data.angle_min_deg < 0) | (data.angle_max_deg > 180) | (data.angle_max_deg <= data.angle_min_deg)).any():
            raise ValueError('Each detector row requires 0 ≤ angle_min_deg < angle_max_deg ≤ 180.')
    for name in ('efficiency','branching_fraction','gamma_efficiency'):
        if name in SCHEMAS[kind] and ((data[name] < 0) | (data[name] > 1)).any():
            raise ValueError(f'{name} must be a fraction between 0 and 1, not a percentage.')
    if kind == 'gamma_counts' and (data.level == 1).any():
        raise ValueError('A direct gamma observation must refer to an excited level, not level 1.')
    if kind == 'probability' and (data.value > 1).any():
        raise ValueError('Population probabilities must lie in [0, 1].')
    if kind == 'cross_section':
        scales = {'barn/sr':1.,'mb/sr':1e-3,'fm²/sr':.01}
        if units not in scales:
            raise ValueError('Choose barn/sr, mb/sr or fm²/sr.')
        data[['value','uncertainty']] *= scales[units]
    return data


def cm_branches(reaction, angle_lab, level_energy):
    """All CM roots for a point on the scattered-projectile lab distribution."""
    tau = reaction.projectile_a/reaction.target_a/np.sqrt(1-level_energy/reaction.energy_cm)
    alpha = np.deg2rad(angle_lab)
    sine = tau*np.sin(alpha)
    if sine > 1+1e-12:
        return []
    delta = np.arcsin(np.clip(sine,-1,1))
    roots = []
    for theta in (alpha+delta, alpha+np.pi-delta):
        degrees = float(np.rad2deg(theta))
        if 0 < degrees <= 180+1e-10:
            degrees = min(degrees,180.)
            if abs(float(lab_angle(reaction,degrees,level_energy))-angle_lab) < 1e-7:
                if not any(abs(degrees-x) < 1e-8 for x in roots):
                    roots.append(degrees)
    for theta in roots:
        if not np.isfinite(lab_jacobian(reaction,np.array([theta]),level_energy)[0]):
            raise ValueError('A measurement lies at a lab turning-point singularity. Use finite detector bins/counts instead of a point cross section.')
    return roots


def compare_measurements(reaction, data, kind, frame='CM', settings=None, stopping=None,
                         exposure=None, order=6, angular_step=1., progress=None):
    """Predict at measured angles, or integrate measured detector acceptance.

    Input is canonical validated data: cross sections already in barn/sr.
    Every unique CM angle is solved directly at each depth, without resampling
    an existing display scan. Detector bins require angular-step convergence.
    """
    data = validate_measurements(data,kind,len(reaction.levels))
    if frame not in ('CM','Lab'):
        raise ValueError('Select CM or Lab angles.')
    if kind=='probability' and frame!='CM':
        raise ValueError('Population comparisons require CM scattering angles.')
    exposure = exposure or Exposure()
    if not math.isfinite(angular_step) or not 0 < angular_step <= 10:
        raise ValueError('Detector integration step must lie in (0, 10] degrees.')
    energies, weights = np.array([reaction.energy_lab]), np.array([1.])
    if stopping is not None:
        _,energies,weights = stopping.quadrature(reaction.energy_lab,exposure.thickness,order)
    plans = []
    counts = kind.endswith('counts')
    if counts and exposure.thickness <= 0:
        raise ValueError('Detector-count comparison requires a positive target thickness.')
    for energy,weight in zip(energies,weights):
        local = reaction.at_energy(float(energy))
        row_angles = []
        for row in data.itertuples():
            level_energy = reaction.levels[row.level-1].energy
            if counts:
                intervals = (detector_cm_intervals(local,row.angle_min_deg,row.angle_max_deg,level_energy)
                             if frame=='Lab' else [(row.angle_min_deg,row.angle_max_deg)])
                nodes = []
                for a,b in intervals:
                    if a <= 0:
                        raise ValueError('A detector bin includes 0° CM, where the Rutherford factor diverges. Use a positive lower acceptance angle.')
                    # Include bin boundaries and at least one interior sample.
                    nodes.extend(angle_grid(a,b,min(angular_step,(b-a)/2)))
                row_angles.append(sorted(set(nodes)))
            else:
                row_angles.append([row.angle_deg] if frame=='CM' else cm_branches(local,row.angle_deg,level_energy))
        angles = sorted({a for nodes in row_angles for a in nodes})
        plans.append((local,weight,row_angles,angles))
    total = sum(len(p[3]) for p in plans)
    if total > 20000:
        raise ValueError(f'This import needs {total:,} collision calculations. Use fewer bins or a larger integration step.')
    predicted = np.zeros(len(data))
    completed = 0
    for local,weight,row_angles,angles in plans:
        if not angles:
            continue
        solver = CoupledChannels(local)
        def update(fraction):
            if progress:
                progress((completed+fraction*len(angles))/max(total,1))
        results = solver.scan(angles, settings or SolverSettings(), update)
        completed += len(angles)
        probabilities = np.array([r.probabilities for r in results])
        sections = cross_sections(local,angles,probabilities)
        lookup = {a:i for i,a in enumerate(angles)}
        for index,row in enumerate(data.itertuples()):
            level = row.level-1
            nodes = row_angles[index]
            if not nodes:
                continue
            indices = [lookup[a] for a in nodes]
            if counts:
                if frame=='Lab':
                    cs = integrate_detector(local,np.array(angles),sections[:,level],row.angle_min_deg,
                                            row.angle_max_deg,reaction.levels[level].energy,exposure.azimuth_fraction)
                else:
                    # The same well-tested integration path with an identity
                    # angle map is not assumed: integrate explicitly in CM.
                    from scipy.integrate import quad
                    from scipy.interpolate import PchipInterpolator
                    rad = np.deg2rad(nodes)
                    interp = PchipInterpolator(rad, sections[indices,level])
                    cs = 2*np.pi*exposure.azimuth_fraction*sum(
                        quad(lambda x: float(interp(x))*np.sin(x),a,b,epsabs=1e-11,epsrel=1e-9)[0]
                        for a,b in zip(rad[:-1],rad[1:]))
                value = particle_yield(cs,local,exposure.thickness,exposure.beam_per_second,exposure.days)*row.efficiency
                if kind=='gamma_counts':
                    value *= row.branching_fraction*row.gamma_efficiency
            elif kind=='probability':
                value = probabilities[indices[0],level]
            elif frame=='CM':
                value = sections[indices[0],level]
            else:
                value = np.sum(sections[indices,level]*lab_jacobian(local,np.asarray(nodes),reaction.levels[level].energy))
            predicted[index] += weight*value
    output = data.copy()
    output['predicted'] = predicted
    output['residual'] = output.value-output.predicted
    output['standardized_residual'] = output.residual/output.uncertainty
    if progress:
        progress(1.)
    return output
