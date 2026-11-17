"""Particle-gamma yields with aligned electric feeding and laboratory response.

Absolute isotropic gamma efficiencies must not be multiplied in again. Nuclear
motion is nonrelativistic, photon boosts exact at that velocity. Input detector
meshes must represent nonoverlapping effective response regions.
"""
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from scipy.integrate import simpson
from .acceptance import particle_intervals
from .decay import validate_network,cascade_densities
from .lab_gamma import GammaMesh,fold_lab_gamma
from .measurements import Exposure,validate_measurements
from .observables import rutherford,particle_yield
from .solver import CoupledChannels,SolverSettings


@dataclass
class GammaResponse:
    detectors: tuple[GammaMesh,...]
    particle_phi_order: int = 16
    boost: bool = True

    def __post_init__(self):
        if not self.detectors or any(not isinstance(d,GammaMesh) for d in self.detectors) or not isinstance(self.particle_phi_order,int) or not 4<=self.particle_phi_order<=256:
            raise ValueError('Supply gamma detector meshes and 4–256 particle azimuth nodes.')
        if not isinstance(self.boost,(bool,np.bool_)):
            raise ValueError('The photon boost option must be a JSON boolean.')
        if sum(d.weights_sr.sum() for d in self.detectors)>4*math.pi*(1+1e-10):
            raise ValueError('Combined gamma response weights exceed 4pi; overlapping detectors would double count photons.')

    @classmethod
    def from_dict(cls,config):
        config=dict(config)
        detectors=[]
        for item in config.pop('detectors'):
            item=dict(item)
            if 'mesh_csv' in item:
                detectors.append(GammaMesh.from_csv(item.pop('mesh_csv'),**item))
            else: detectors.append(GammaMesh.annulus(**item))
        return cls(tuple(detectors),**config)


def predict_lab_gamma(reaction,data,transitions,photon_transition,response,frame='CM',settings=None,
                      stopping=None,exposure=None,order=6,angular_step=1.,detected_particle='projectile',
                      particle_acceptance=None,particle_energy_min_mev=0.):
    """Each initial-level density has its own Rutherford factor and acceptance.

    Particle azimuth is integrated over the complete annulus. A fractional
    azimuth normalization without a specified mask is rejected for this model.
    """
    validate_network(reaction,transitions)
    if not 0<=photon_transition<len(transitions): raise ValueError('Select an existing photon transition.')
    edge=transitions[photon_transition]
    if 'level' in data and not (data.level==edge.upper+1).all():
        raise ValueError('Photon-count level must identify the parent of the selected photon transition.')
    data=data.copy();data['level']=edge.upper+1
    data=validate_measurements(data,'particle_counts',len(reaction.levels))
    if 'gamma_efficiency' in data and not np.allclose(pd.to_numeric(data.gamma_efficiency,errors='coerce'),1.,atol=0.,rtol=0.):
        raise ValueError('Use gamma_efficiency=1 with a laboratory gamma response to avoid counting efficiency twice.')
    if frame not in ('CM','Lab') or detected_particle not in ('projectile','recoil','either'):
        raise ValueError('Specify CM/Lab finite bins and a valid detected particle.')
    exposure=exposure or Exposure()
    if exposure.thickness<=0 or exposure.azimuth_fraction!=1:
        raise ValueError('Lab gamma response needs a positive target thickness and full particle azimuth coverage; arbitrary masks are not modeled.')
    if not np.isfinite(angular_step) or not 0<angular_step<=10:
        raise ValueError('Angular integration step must lie in (0,10] degrees.')
    settings=settings or SolverSettings()
    energies,weights=np.array([reaction.energy_lab]),np.array([1.])
    if stopping is not None: _,energies,weights=stopping.quadrature(reaction.energy_lab,exposure.thickness,order)
    predicted=np.zeros(len(data))
    phi=(np.arange(response.particle_phi_order)+.5)*2*math.pi/response.particle_phi_order
    for energy,depth_weight in zip(energies,weights):
        local=reaction.at_energy(float(energy));solver=CoupledChannels(local);collision_cache={};density_cache={}
        plans=[]
        for row in data.itertuples():
            row_plan=[]
            for initial in range(1,len(local.levels)):
                exit_energy=local.levels[initial].energy
                if frame=='Lab':
                    lo,hi=row.angle_min_deg,row.angle_max_deg
                    if particle_acceptance is not None: lo,hi=max(lo,particle_acceptance[0]),min(hi,particle_acceptance[1])
                    intervals=particle_intervals(local,lo,hi,exit_energy,detected_particle,particle_energy_min_mev) if hi>lo else []
                elif particle_acceptance is not None:
                    accepted=particle_intervals(local,*particle_acceptance,exit_energy,detected_particle,particle_energy_min_mev)
                    intervals=[(max(a,row.angle_min_deg),min(b,row.angle_max_deg)) for a,b in accepted]
                    intervals=[(a,b) for a,b in intervals if b>a]
                else:
                    if particle_energy_min_mev: raise ValueError('An energy threshold on CM bins needs particle_acceptance.')
                    intervals=[(row.angle_min_deg,row.angle_max_deg)]
                for a,b in intervals:
                    if a<=0: raise ValueError('The accepted particle bin includes zero CM angle.')
                    panels=max(2,2*math.ceil((b-a)/(2*angular_step)))
                    row_plan.append((initial,np.linspace(a,b,panels+1)))
            plans.append(row_plan)
        all_angles=sorted({float(theta) for plan in plans for _,nodes in plan for theta in nodes})
        if len(all_angles)>20000: raise ValueError('Lab gamma integration needs too many collision angles.')
        for angle in all_angles: collision_cache[angle]=solver.solve(angle,settings)
        for row_index,(row,plan) in enumerate(zip(data.itertuples(),plans)):
            cross_section=0.
            for initial,nodes in plan:
                values=[]
                for angle in nodes:
                    key=(initial,float(angle))
                    if key not in density_cache:
                        collision=collision_cache[float(angle)]
                        seeds=[np.zeros_like(rho) for rho in collision.density_matrices]
                        seeds[initial]=collision.density_matrices[initial]*float(rutherford(local,angle,local.levels[initial].energy))
                        fed=cascade_densities(local,seeds,transitions)[edge.upper]
                        value=0.
                        for azimuth in phi:
                            for detector in response.detectors:
                                value+=fold_lab_gamma(local,np.deg2rad(angle),fed,edge.upper,edge.lower,
                                    edge.multipolarity,detector,particle_phi=azimuth,
                                    exit_energy=local.levels[initial].energy,boost=response.boost)
                        density_cache[key]=value/len(phi)*edge.branch/(1+edge.alpha)
                    values.append(density_cache[key])
                radians=np.deg2rad(nodes)
                cross_section+=2*math.pi*simpson(np.asarray(values)*np.sin(radians),x=radians)
            predicted[row_index]+=depth_weight*particle_yield(cross_section,local,exposure.thickness,
                                              exposure.beam_per_second,exposure.days)*row.efficiency
    return predicted
