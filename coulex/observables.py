"""Cross sections, lab kinematics, safe separation and thin-target yields."""

import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import PchipInterpolator


def rutherford(reaction, angles, level_energy=0.0):
    """Level-dependent Rutherford factor in barn/sr (not fm²/sr)."""
    angles = np.asarray(angles, float)
    if np.any(~np.isfinite(angles)) or np.any((angles <= 0) | (angles > 180)):
        raise ValueError("Rutherford angles must lie in (0, 180].")
    if not np.isfinite(level_energy) or not 0 <= level_energy < reaction.energy_cm:
        raise ValueError("Excitation energy must lie below E_cm.")
    epsilon = 1/np.sin(np.deg2rad(angles)/2)
    velocity_factor = 1/np.sqrt(1-level_energy/reaction.energy_cm)
    return 0.000625*reaction.head_on_distance**2*epsilon**4*velocity_factor


def cross_sections(reaction, angles, probabilities):
    probabilities = np.asarray(probabilities)
    if probabilities.shape != (len(angles), len(reaction.levels)):
        raise ValueError("Probabilities must have shape (number of angles, number of levels).")
    return probabilities*np.column_stack([rutherford(reaction, angles, x.energy) for x in reaction.levels])


def lab_angle(reaction, theta_cm, level_energy=0.0):
    """Scattered projectile angle, including the reduced exit-channel speed."""
    if not 0 <= level_energy < reaction.energy_cm:
        raise ValueError("The exit channel must be open.")
    theta = np.deg2rad(theta_cm)
    tau = reaction.projectile_a/reaction.target_a/np.sqrt(1-level_energy/reaction.energy_cm)
    return np.rad2deg(np.arctan2(np.sin(theta), np.cos(theta)+tau))


def lab_jacobian(reaction, theta_cm, level_energy=0.0):
    """dΩ_cm/dΩ_lab for each branch. Singular turning points are returned as NaN."""
    theta = np.deg2rad(theta_cm)
    tau = reaction.projectile_a/reaction.target_a/np.sqrt(1-level_energy/reaction.energy_cm)
    numerator = np.maximum(0, 1+tau*tau+2*tau*np.cos(theta))**1.5
    denominator = abs(1+tau*np.cos(theta))
    return np.divide(numerator, denominator, out=np.full_like(theta, np.nan), where=denominator > 1e-12)


def distance_of_closest_approach(reaction, angles):
    return reaction.head_on_distance*(1+1/np.sin(np.deg2rad(angles)/2))/2


def surface_separation(reaction, angles):
    # Nuclear radii scale with the cube root of the mass number.
    contact = 1.25*(np.cbrt(reaction.projectile_a)+np.cbrt(reaction.target_a))
    return distance_of_closest_approach(reaction, angles)-contact


def detector_cm_intervals(reaction, lab_min, lab_max, level_energy=0.0):
    """Invert a projectile lab annulus, retaining BOTH inverse-kinematics branches."""
    if not 0 <= lab_min < lab_max <= 180:
        raise ValueError("Require 0 ≤ detector minimum < maximum ≤ 180°.")
    tau = reaction.projectile_a/reaction.target_a/np.sqrt(1-level_energy/reaction.energy_cm)
    boundaries = [0., 180.]
    if tau > 1:
        boundaries.append(float(np.rad2deg(np.arccos(-1/tau))))
    for alpha in (lab_min, lab_max):
        ar = np.deg2rad(alpha)
        sine = tau*np.sin(ar)
        if sine <= 1+1e-12:
            delta = np.arcsin(np.clip(sine, -1, 1))
            for theta in (ar+delta, ar+np.pi-delta):
                degrees = float(np.rad2deg(theta))
                if 0 <= degrees <= 180 and abs(float(lab_angle(reaction, degrees, level_energy))-alpha) < 1e-6:
                    boundaries.append(degrees)
    boundaries = sorted(set(boundaries))
    return [(a, b) for a, b in zip(boundaries[:-1], boundaries[1:])
            if lab_min <= lab_angle(reaction, (a+b)/2, level_energy) <= lab_max and b-a > 1e-10]


def integrate_detector(reaction, angles, differential_cs, lab_min, lab_max, level_energy=0.0,
                       azimuth_fraction=1.0):
    """Integrate in CM solid angle, avoiding lab caustic singularities.

    PCHIP interpolates dσ/dΩ on the supplied grid. The angular discretization
    must be checked by recalculation on a finer grid; interpolation is not a solver.
    """
    angles, cs = np.asarray(angles, float), np.asarray(differential_cs, float)
    if angles.ndim != 1 or len(angles) < 2 or np.any(np.diff(angles) <= 0) or cs.shape != angles.shape:
        raise ValueError("Detector integration needs at least two ordered angle samples.")
    if np.any(~np.isfinite(cs)) or np.any(cs < 0) or not 0 <= azimuth_fraction <= 1:
        raise ValueError("Cross sections must be nonnegative and azimuth coverage must lie in [0, 1].")
    intervals = detector_cm_intervals(reaction, lab_min, lab_max, level_energy)
    interpolator = PchipInterpolator(np.deg2rad(angles), cs, extrapolate=False)
    total = 0.0
    for a, b in intervals:
        if a < angles[0]-1e-7 or b > angles[-1]+1e-7:
            raise ValueError(f"Detector requires CM angles {a:.3f}–{b:.3f}°; extend the calculated grid.")
        # Integrate the cubic interpolant times sin(theta) with fine Simpson panels.
        grid = np.linspace(np.deg2rad(max(a, angles[0])), np.deg2rad(min(b, angles[-1])),
                           max(65, int((b-a)/0.05)*2+1))
        total += 2*np.pi*simpson(interpolator(grid)*np.sin(grid), x=grid)
    return float(total*azimuth_fraction)


def particle_yield(cross_section_barn, reaction, thickness_mg_cm2=2.0, beam_per_second=1e5, days=5.0):
    """Thin-target populations; no branching ratios or gamma efficiency implied."""
    values = (cross_section_barn, thickness_mg_cm2, beam_per_second, days)
    if not all(np.isfinite(x) and x >= 0 for x in values):
        raise ValueError("Yield inputs must be finite and nonnegative.")
    target_atoms = thickness_mg_cm2*1e-3/reaction.target_a*6.02214076e23
    return cross_section_barn*1e-24*target_atoms*beam_per_second*days*86400
