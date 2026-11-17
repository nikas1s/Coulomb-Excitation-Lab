"""Two-body recoil acceptance and event-wise particle-detector unions.

The union assumes one event counted once when either partner reaches the same
annulus. It does not model per-strip efficiency, different azimuth masks or
experimental coincidence/trigger logic.
"""
import numpy as np
import pandas as pd
from .observables import detector_cm_intervals
from .measurements import compare_measurements,validate_measurements,Exposure


def recoil_lab_angle(reaction, theta_cm, level_energy=0.):
    if not np.isfinite(level_energy) or not 0 <= level_energy < reaction.energy_cm:
        raise ValueError('The recoil exit channel must be open.')
    theta=np.deg2rad(np.asarray(theta_cm,float))
    f=np.sqrt(1-level_energy/reaction.energy_cm)
    numerator=f*np.sin(theta);denominator=(1-f)+2*f*np.sin(theta/2)**2
    angle=np.degrees(np.arctan2(numerator,denominator))
    return np.where((numerator==0)&(denominator==0),np.nan,angle)


def recoil_jacobian(reaction,theta_cm,level_energy=0.):
    if not np.isfinite(level_energy) or not 0 <= level_energy < reaction.energy_cm:
        raise ValueError('The recoil exit channel must be open.')
    theta=np.deg2rad(np.asarray(theta_cm,float))
    f=np.sqrt(1-level_energy/reaction.energy_cm)
    radius=((1-f)**2+4*f*np.sin(theta/2)**2)**1.5
    denominator=f*f*abs(np.cos(theta)-f)
    return np.divide(radius,denominator,out=np.full_like(theta,np.nan),where=denominator>1e-12)


def recoil_cm_roots(reaction,angle_lab,level_energy=0.):
    if not np.isfinite(angle_lab) or not 0 <= angle_lab <= 180:
        raise ValueError('Recoil lab angle must lie in [0,180].')
    if not np.isfinite(level_energy) or not 0 <= level_energy < reaction.energy_cm:
        raise ValueError('The recoil exit channel must be open.')
    f=np.sqrt(1-level_energy/reaction.energy_cm)
    if angle_lab>90: return []
    alpha=np.deg2rad(angle_lab)
    sine=np.sin(alpha)/f
    if sine>1+1e-12: return []
    delta=np.arcsin(np.clip(sine,-1,1))
    roots=[]
    for theta in (delta-alpha,np.pi-delta-alpha):
        value=float(np.degrees(theta))
        if 0<value<=180+1e-9 and not any(abs(value-x)<1e-8 for x in roots):
            value=min(value,180.)
            if abs(float(recoil_lab_angle(reaction,value,level_energy))-angle_lab)<1e-7:
                roots.append(value)
    return sorted(roots)


def _merge(intervals):
    result=[]
    for a,b in sorted(intervals):
        if result and a<=result[-1][1]+1e-10:
            result[-1]=(result[-1][0],max(result[-1][1],b))
        else: result.append((a,b))
    return result


def particle_energy(reaction,theta_cm,level_energy=0.,detected_particle='recoil'):
    if not np.isfinite(level_energy) or not 0 <= level_energy < reaction.energy_cm:
        raise ValueError('The recoil exit channel must be open.')
    if detected_particle not in ('projectile','recoil'):
        raise ValueError('Choose one particle for its kinetic energy.')
    f=np.sqrt(1-level_energy/reaction.energy_cm)
    a,b=reaction.projectile_a,reaction.target_a
    theta=np.deg2rad(theta_cm)
    if detected_particle=='recoil':
        return reaction.energy_lab*a*b/(a+b)**2*((1-f)**2+4*f*np.sin(theta/2)**2)
    return reaction.energy_lab/(a+b)**2*((a-b*f)**2+4*a*b*f*np.cos(theta/2)**2)


def particle_intervals(reaction,lab_min,lab_max,level_energy=0.,detected_particle='recoil',energy_min_mev=0.):
    if detected_particle not in ('projectile','recoil','either'):
        raise ValueError('Detected particle must be projectile, recoil or either.')
    if not np.isfinite(level_energy) or not 0 <= level_energy < reaction.energy_cm:
        raise ValueError('The recoil exit channel must be open.')
    if not np.isfinite(energy_min_mev) or energy_min_mev<0:
        raise ValueError('Particle energy threshold must be finite and nonnegative.')
    if not 0<=lab_min<lab_max<=180:
        raise ValueError('Require 0 <= detector minimum < maximum <= 180 degrees.')
    if detected_particle=='either':
        return _merge(
            particle_intervals(reaction,lab_min,lab_max,level_energy,'projectile',energy_min_mev)+
            particle_intervals(reaction,lab_min,lab_max,level_energy,'recoil',energy_min_mev))
    if detected_particle=='projectile':
        intervals=detector_cm_intervals(reaction,lab_min,lab_max,level_energy)
    else:
        f=np.sqrt(1-level_energy/reaction.energy_cm)
        nodes=[0.,180.,float(np.degrees(np.arccos(f)))]
        for edge in (lab_min,lab_max): nodes.extend(recoil_cm_roots(reaction,edge,level_energy))
        nodes=sorted(set(nodes))
        intervals=[(a,b) for a,b in zip(nodes[:-1],nodes[1:]) if b-a>1e-10 and
                   lab_min<=recoil_lab_angle(reaction,(a+b)/2,level_energy)<=lab_max]
    if energy_min_mev:
        from scipy.optimize import brentq
        e0=float(particle_energy(reaction,0.,level_energy,detected_particle))
        e180=float(particle_energy(reaction,180.,level_energy,detected_particle))
        if energy_min_mev>max(e0,e180): return []
        if energy_min_mev>min(e0,e180):
            boundary=brentq(lambda theta:float(particle_energy(reaction,theta,level_energy,detected_particle))-energy_min_mev,0.,180.)
            intervals=[(max(a,boundary),b) if detected_particle=='recoil' else (a,min(b,boundary)) for a,b in intervals]
            intervals=[(a,b) for a,b in intervals if b>a]
    return _merge(intervals)


def compare_particle_acceptance(reaction,data,kind,frame='CM',settings=None,stopping=None,
                                exposure=None,order=6,angular_step=1.,detected_particle='recoil',particle_acceptance=None,particle_energy_min_mev=0.):
    """Finite count bins with projectile/recoil/either acceptance, at each depth.

    If CM bins have an additional lab annulus, intersect each CM bin with the
    accepted event intervals. Otherwise CM count bins represent full acceptance.
    Lab point cross sections require a separate recoil Jacobian treatment and
    are intentionally rejected by this finite-bin API.
    """
    data=validate_measurements(data,kind,len(reaction.levels))
    if frame not in ('CM','Lab') or not kind.endswith('counts'):
        raise ValueError('Recoil/either acceptance requires finite CM or Lab count bins.')
    if detected_particle not in ('projectile','recoil','either'):
        raise ValueError('Detected particle must be projectile, recoil or either.')
    exposure=exposure or Exposure()
    energies,weights=np.array([reaction.energy_lab]),np.array([1.])
    if stopping is not None:
        _,energies,weights=stopping.quadrature(reaction.energy_lab,exposure.thickness,order)
    predicted=np.zeros(len(data))
    for energy,weight in zip(energies,weights):
        local=reaction.at_energy(float(energy));records=[];owners=[]
        for index,row in enumerate(data.to_dict('records')):
            level_energy=local.levels[int(row['level'])-1].energy
            if frame=='Lab':
                low,high=row['angle_min_deg'],row['angle_max_deg']
                if particle_acceptance is not None:
                    low,high=max(low,particle_acceptance[0]),min(high,particle_acceptance[1])
                intervals=particle_intervals(local,low,high,level_energy,detected_particle,particle_energy_min_mev) if high>low else []
            elif particle_acceptance is not None:
                intervals=particle_intervals(local,*particle_acceptance,level_energy,detected_particle,particle_energy_min_mev)
                intervals=[(max(a,row['angle_min_deg']),min(b,row['angle_max_deg'])) for a,b in intervals]
                intervals=[(a,b) for a,b in intervals if b>a]
            else:
                if particle_energy_min_mev:
                    raise ValueError('An energy threshold on CM bins requires an explicit lab particle_acceptance.')
                intervals=[(row['angle_min_deg'],row['angle_max_deg'])]
            for a,b in intervals:
                if a<=0: raise ValueError('Accepted recoil bin includes 0 degrees CM; use a positive lower acceptance.')
                records.append({**row,'angle_min_deg':a,'angle_max_deg':b});owners.append(index)
        if records:
            values=compare_measurements(local,pd.DataFrame(records),kind,'CM',settings,None,exposure,order,angular_step).predicted
            np.add.at(predicted,owners,weight*values.to_numpy())
    result=data.copy();result['predicted']=predicted
    result['residual']=result.value-result.predicted
    result['standardized_residual']=result.residual/result.uncertainty
    return result
