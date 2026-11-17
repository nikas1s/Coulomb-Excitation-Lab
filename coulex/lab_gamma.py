"""Pure-electric photon response in laboratory coordinates.

Nuclear velocities follow the app's nonrelativistic two-body kinematics; photon
aberration/Doppler factors use an exact Lorentz boost at that velocity. Nuclear
recoil from prior gamma emissions and finite decay flight distances are not
included. Efficiencies are intrinsic probabilities for photons incident along
each mesh direction, not absolute isotropic efficiencies of the full array.
"""
from dataclasses import dataclass
from io import StringIO
import math
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from .decay import emission_operators,small_d,validate_density

AMU=931.49410242


def orbit_to_lab(theta_cm,particle_phi=0.,excitation='projectile'):
    """Proper rotation; theta/phi radians, beam on lab +z, projectile deflects at phi."""
    if not np.isfinite(theta_cm+particle_phi) or not 0<theta_cm<=math.pi or excitation not in ('projectile','target'):
        raise ValueError('Invalid collision orientation.')
    s,c=math.sin(theta_cm/2),math.cos(theta_cm/2)
    basis=np.array([[0.,1.,0.],[s,0.,c],[c,0.,-s]])
    # Rows of basis.T map orbit coordinates to the collision-plane lab frame.
    matrix=basis.T
    if excitation=='target': matrix=np.diag([-1.,1.,-1.])@matrix
    cp,sp=math.cos(particle_phi),math.sin(particle_phi)
    return np.array([[cp,-sp,0.],[sp,cp,0.],[0.,0.,1.]])@matrix


def emitter_beta(reaction,theta_cm,exit_energy,particle_phi=0.):
    if not np.isfinite(theta_cm+particle_phi) or not 0<theta_cm<=math.pi:
        raise ValueError('Invalid collision orientation.')
    if not np.isfinite(exit_energy) or not 0<=exit_energy<reaction.energy_cm:
        raise ValueError('The emitting exit channel must be open.')
    mp,mt=AMU*reaction.projectile_a,AMU*reaction.target_a
    p0=math.sqrt(2*mp*reaction.energy_lab);boost=p0/(mp+mt)
    momentum=p0*mt/(mp+mt)*math.sqrt(1-exit_energy/reaction.energy_cm)
    speed=momentum/mp if reaction.excitation=='projectile' else -momentum/mt
    vector=np.array([speed*math.sin(theta_cm)*math.cos(particle_phi),
                     speed*math.sin(theta_cm)*math.sin(particle_phi),boost+speed*math.cos(theta_cm)])
    if np.linalg.norm(vector)>=1:
        raise ValueError('Nonrelativistic nuclear kinematics gives an invalid emission velocity.')
    return vector


def inverse_photon_boost(directions,beta):
    """Return rest-frame unit directions and E_lab/E_rest for lab directions."""
    directions=np.asarray(directions,float);beta=np.asarray(beta,float)
    if directions.ndim!=2 or directions.shape[1]!=3 or beta.shape!=(3,) or not np.all(np.isfinite(directions)) or not np.all(np.isfinite(beta)):
        raise ValueError('Invalid photon directions or velocity.')
    if not np.allclose(np.linalg.norm(directions,axis=1),1.,rtol=0.,atol=1e-12):
        raise ValueError('Photon directions must be unit vectors.')
    b2=float(beta@beta)
    if b2>=1: raise ValueError('Emission speed must be below c.')
    if b2==0: return directions.copy(),np.ones(len(directions))
    gamma=1/math.sqrt(1-b2);dot=directions@beta
    denominator=gamma*(1-dot)
    # (gamma-1)/beta² = gamma²/(gamma+1), stable for slow nuclei.
    coefficient=gamma*gamma/(gamma+1)*dot-gamma
    rest=(directions+coefficient[:,None]*beta)/denominator[:,None]
    return rest,1/denominator


@dataclass
class GammaMesh:
    directions: np.ndarray
    weights_sr: np.ndarray
    intrinsic_efficiency: np.ndarray
    energy_mev: object = None
    efficiency_curve: object = None

    def __post_init__(self):
        self.directions=np.asarray(self.directions,float)
        n=len(self.directions)
        self.weights_sr=np.asarray(self.weights_sr,float)
        self.intrinsic_efficiency=np.broadcast_to(np.asarray(self.intrinsic_efficiency,float),(n,)).copy()
        if self.directions.shape!=(n,3) or not n or not np.all(np.isfinite(self.directions)) or not np.allclose(np.linalg.norm(self.directions,axis=1),1.,atol=1e-12,rtol=0.):
            raise ValueError('Gamma mesh needs finite unit directions.')
        if self.weights_sr.shape!=(n,) or np.any(~np.isfinite(self.weights_sr)) or np.any(self.weights_sr<=0) or self.weights_sr.sum()>4*math.pi*(1+1e-10):
            raise ValueError('Gamma solid-angle weights must be positive and sum to at most 4pi.')
        if np.any(~np.isfinite(self.intrinsic_efficiency)) or np.any((self.intrinsic_efficiency<0)|(self.intrinsic_efficiency>1)):
            raise ValueError('Intrinsic photon efficiencies must lie in [0,1].')
        if (self.energy_mev is None)!=(self.efficiency_curve is None):
            raise ValueError('Supply both energy and efficiency curve arrays.')
        self.curve=None
        if self.energy_mev is not None:
            energy=np.asarray(self.energy_mev,float);eff=np.asarray(self.efficiency_curve,float)
            if energy.ndim!=1 or len(energy)<2 or energy.shape!=eff.shape or np.any(~np.isfinite(energy)) or np.any(energy<=0) or np.any(np.diff(energy)<=0) or np.any(~np.isfinite(eff)) or np.any((eff<0)|(eff>1)):
                raise ValueError('Gamma energy calibration needs increasing positive energies and efficiencies in [0,1].')
            self.energy_mev=energy;self.curve=PchipInterpolator(energy,eff,extrapolate=False)

    @classmethod
    def annulus(cls,theta_min_deg,theta_max_deg,phi_min_deg=0.,phi_max_deg=360.,efficiency=1.,order=16,phi_order=32,**curve):
        if not 0<=theta_min_deg<theta_max_deg<=180 or not 0<=phi_min_deg<phi_max_deg<=360 or not isinstance(order,int) or not 4<=order<=128 or not isinstance(phi_order,int) or not 4<=phi_order<=512:
            raise ValueError('Invalid gamma detector annulus or quadrature order.')
        nodes,weights=np.polynomial.legendre.leggauss(order)
        lo,hi=np.cos(np.deg2rad(theta_max_deg)),np.cos(np.deg2rad(theta_min_deg))
        x=(lo+hi)/2+(hi-lo)/2*nodes;wx=(hi-lo)/2*weights
        a,b=np.deg2rad([phi_min_deg,phi_max_deg])
        if abs(b-a-2*math.pi)<1e-12:
            phi=a+(np.arange(phi_order)+.5)*(b-a)/phi_order;wp=np.full(phi_order,(b-a)/phi_order)
        else:
            nodes,weights=np.polynomial.legendre.leggauss(phi_order)
            phi=(a+b)/2+(b-a)/2*nodes;wp=(b-a)/2*weights
        xx,pp=np.meshgrid(x,phi,indexing='ij')
        directions=np.stack([np.sqrt(1-xx*xx)*np.cos(pp),np.sqrt(1-xx*xx)*np.sin(pp),xx],axis=-1).reshape(-1,3)
        return cls(directions,np.outer(wx,wp).ravel(),efficiency,**curve)

    @classmethod
    def from_csv(cls,text,**curve):
        frame=pd.read_csv(StringIO(text))
        required=['theta_deg','phi_deg','weight_sr','intrinsic_efficiency']
        if not set(required)<=set(frame): raise ValueError('Gamma mesh CSV needs theta_deg,phi_deg,weight_sr,intrinsic_efficiency.')
        try: values=frame[required].astype(float)
        except (ValueError,TypeError) as error: raise ValueError('Gamma mesh columns must be numeric.') from error
        if not np.isfinite(values.to_numpy()).all() or not values.theta_deg.between(0,180).all() or not values.phi_deg.between(0,360).all():
            raise ValueError('Gamma mesh angles must be finite and inside their physical ranges.')
        theta,phi=np.deg2rad(values.theta_deg),np.deg2rad(values.phi_deg)
        directions=np.column_stack([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
        return cls(directions,values.weight_sr.to_numpy(),values.intrinsic_efficiency.to_numpy(),**curve)


def angular_kernel(density,ji,jf,lam):
    rho=validate_density(density,ji)
    if lam not in (1,2,3,4) or not abs(ji-jf)<=lam<=ji+jf:
        raise ValueError('Invalid electric photon angular momentum.')
    operators=emission_operators(ji,jf,lam)
    return np.array([[np.trace(a@rho@b.conj().T) for b in operators] for a in operators])


def angular_density(kernel,lam,directions):
    polar=np.arccos(np.clip(directions[:,2],-1,1));phi=np.arctan2(directions[:,1],directions[:,0])
    q=np.arange(-lam,lam+1);phase=np.exp(1j*phi[:,None]*q)
    result=np.zeros(len(directions))
    for helicity in (-1,1):
        d=np.stack([small_d(lam,int(m),helicity,polar) for m in q],axis=-1)
        coefficient=phase*d
        result+=np.einsum('nq,qr,nr->n',coefficient,kernel,coefficient.conj()).real
    return result*(2*lam+1)/(8*math.pi)


def fold_lab_gamma(reaction,theta_cm,density,upper,lower,lam,detector,particle_phi=0.,exit_energy=None,boost=True):
    """Photon detection probability for one collision plane; angles in radians."""
    if not 0<=lower<len(reaction.levels) or not 0<=upper<len(reaction.levels):
        raise ValueError('Invalid gamma transition levels.')
    parent,daughter=reaction.levels[upper],reaction.levels[lower]
    energy=parent.energy-daughter.energy
    if energy<=0 or parent.parity*daughter.parity!=(-1)**lam:
        raise ValueError('The gamma transition must decrease energy and satisfy electric parity.')
    kernel=angular_kernel(density,parent.spin,daughter.spin,lam)
    rotation=orbit_to_lab(theta_cm,particle_phi,reaction.excitation)
    if not np.any(kernel): return 0.
    beta=emitter_beta(reaction,theta_cm,parent.energy if exit_energy is None else exit_energy,particle_phi) if boost else np.zeros(3)
    directions,doppler=inverse_photon_boost(detector.directions,beta)
    orbit=directions@rotation
    response=angular_density(kernel,lam,orbit)*doppler**2
    efficiency=detector.intrinsic_efficiency
    if detector.curve is not None:
        shifted=energy*doppler
        if np.any(shifted<detector.energy_mev[0]) or np.any(shifted>detector.energy_mev[-1]):
            raise ValueError('Doppler-shifted photons leave the supplied efficiency calibration range.')
        efficiency=efficiency*detector.curve(shifted)
    return float(np.dot(detector.weights_sr,response*efficiency))
