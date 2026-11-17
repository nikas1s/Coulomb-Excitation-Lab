"""Acyclic decay networks and pure-electric photon density-matrix response.

All branches are TOTAL decay probabilities; photon probability is branch/(1+α).
Alpha is supplied evaluated data, not calculated. No mixed-multipole interference,
finite flight-distance efficiency, hyperfine deorientation or Lorentz boost.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import factorial, sqrt, pi
import numpy as np
import pandas as pd
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan
from .shapes import reduced


@dataclass(frozen=True)
class Transition:
    upper: int
    lower: int
    branch: float
    alpha: float = 0.
    multipolarity: int = 2

    def __post_init__(self):
        if any(not isinstance(v,(int,np.integer)) for v in (self.upper,self.lower,self.multipolarity)):
            raise ValueError('Decay indices and multipolarity must be integers.')


def validate_network(reaction, transitions):
    seen = set()
    totals = {}
    for edge in transitions:
        if not 0 <= edge.upper < len(reaction.levels) or not 0 <= edge.lower < len(reaction.levels):
            raise ValueError('Decay level index is outside the model.')
        u,l = reaction.levels[edge.upper], reaction.levels[edge.lower]
        if u.energy <= l.energy or (edge.upper,edge.lower) in seen:
            raise ValueError('Decay edges must be unique and decrease energy.')
        if not np.isfinite(edge.branch) or not 0 <= edge.branch <= 1 or not np.isfinite(edge.alpha) or edge.alpha < 0:
            raise ValueError('Branches must lie in [0,1]; conversion coefficients must be nonnegative.')
        if edge.multipolarity not in (1,2,3,4) or not abs(u.spin-l.spin) <= edge.multipolarity <= u.spin+l.spin or u.parity*l.parity != (-1)**edge.multipolarity:
            raise ValueError('Decay edge violates pure-electric selection rules.')
        seen.add((edge.upper,edge.lower))
        totals[edge.upper] = totals.get(edge.upper,0)+edge.branch
    if any(v > 1+1e-12 for v in totals.values()):
        raise ValueError('Outgoing total decay branches cannot exceed one.')
    return {i:1-totals.get(i,0.) for i in range(len(reaction.levels)) if i and totals.get(i,0.) < 1-1e-12}


def cascade(reaction, populations, transitions):
    """Integrated emitted photons per collision; incomplete branches remain sinks."""
    validate_network(reaction,transitions)
    occupancy = np.array(populations,float,copy=True)
    if occupancy.shape != (len(reaction.levels),) or np.any(~np.isfinite(occupancy)) or np.any(occupancy < 0):
        raise ValueError('Supply a finite nonnegative population for every level.')
    photons = np.zeros(len(transitions))
    for upper in sorted(range(len(reaction.levels)),key=lambda i:reaction.levels[i].energy,reverse=True):
        for k,edge in enumerate(transitions):
            if edge.upper == upper:
                flow = occupancy[upper]*edge.branch
                photons[k] = flow/(1+edge.alpha)
                occupancy[edge.lower] += flow
    return occupancy, photons


def electric_rate(energy_mev, strength, lam):
    """Photon partial rate s^-1, B(Eλ; upper→lower) in e² b^λ.

    Multipole radiation formula with CODATA ħ and ħc, e²/(4πε0).
    """
    if lam not in (1,2,3,4) or not np.isfinite(energy_mev) or energy_mev <= 0 or not np.isfinite(strength) or strength < 0:
        raise ValueError('Require positive transition energy and nonnegative electric strength.')
    double_factorial = np.prod(np.arange(1,2*lam+2,2,dtype=float))
    return 8*pi*(lam+1)/(lam*double_factorial**2)*(energy_mev/197.3269804)**(2*lam+1)*1.439964548/6.582119569e-22*strength*100**lam


def decay_rates(reaction, alphas=None):
    """Rates implied by all nonzero off-diagonal electric matrix elements."""
    alphas = alphas or {}
    rows = []
    for edge in reaction.elements:
        a,b = edge.initial,edge.final
        if a == b or not edge.value:
            continue
        upper,lower = sorted((a,b),key=lambda i:reaction.levels[i].energy,reverse=True)
        energy = reaction.levels[upper].energy-reaction.levels[lower].energy
        strength = reduced(reaction,upper,lower,edge.multipolarity)**2/(2*reaction.levels[upper].spin+1)
        photon_rate = electric_rate(energy,strength,edge.multipolarity)
        alpha = alphas.get((upper,lower),0.)
        if not np.isfinite(alpha) or alpha < 0:
            raise ValueError('Conversion coefficients must be nonnegative.')
        rows.append(dict(upper=upper+1,lower=lower+1,E_mev=energy,lam=edge.multipolarity,
                         B_down=strength,photon_rate_s=photon_rate,total_rate_s=photon_rate*(1+alpha)))
    frame = pd.DataFrame(rows,columns=['upper','lower','E_mev','lam','B_down','photon_rate_s','total_rate_s'])
    if not frame.empty:
        totals = frame.groupby('upper').total_rate_s.transform('sum')
        frame['total_branch'] = frame.total_rate_s/totals
        frame['lifetime_ps'] = 1e12/totals
    return frame


@lru_cache(maxsize=128)
def emission_operators(ji, jf, lam):
    """Kq[mf,mi]=<Jf mf,L q|Ji mi>; sum Kq† Kq=I."""
    mi,mf = np.arange(-ji,ji+1),np.arange(-jf,jf+1)
    operators = []
    for q in range(-lam,lam+1):
        op = np.zeros((len(mf),len(mi)))
        for row,m in enumerate(mf):
            for col,n in enumerate(mi):
                if abs(m+q-n) < 1e-10:
                    op[row,col] = float(clebsch_gordan(Rational(int(2*jf),2),lam,Rational(int(2*ji),2),
                                      Rational(int(2*m),2),q,Rational(int(2*n),2)))
        operators.append(op)
    return np.asarray(operators)


def small_d(j, m, n, theta):
    """Integer-j Wigner small d via finite factorial sum (j≤4)."""
    value = 0.
    prefactor = sqrt(factorial(j+m)*factorial(j-m)*factorial(j+n)*factorial(j-n))
    for k in range(2*j+1):
        den = (j+n-k,k,m-n+k,j-m-k)
        if min(den) >= 0:
            value += (-1)**(m-n+k)*prefactor/np.prod([factorial(x) for x in den])*np.cos(theta/2)**(2*j+n-m-2*k)*np.sin(theta/2)**(m-n+2*k)
    return value


def validate_density(density,spin):
    """Validate in relative units, including arbitrarily small cross-section blocks."""
    rho=np.asarray(density,complex);size=int(2*spin+1)
    if rho.shape!=(size,size) or not np.all(np.isfinite(rho)):
        raise ValueError('Emission requires a positive Hermitian spin density matrix.')
    scale=float(np.max(abs(rho)))
    if scale and (not np.allclose(rho,rho.conj().T,atol=1e-14*scale,rtol=1e-10)
                  or np.linalg.eigvalsh(rho/scale).min() < -1e-12):
        raise ValueError('Emission requires a positive Hermitian spin density matrix.')
    return rho


def photon_map(density, ji, jf, lam, theta, phi):
    """Unpolarized photon response, per sr; angles radians in emitting rest frame.

    z is the solver orbit quantization axis; the scattering plane is yz and x is its normal.
    Trace is photon angular density, output is conditional daughter density.
    """
    rho = validate_density(density,ji)
    if not 0 <= theta <= pi or not np.isfinite(phi):
        raise ValueError('Photon angles must be finite with theta in [0,pi].')
    if not abs(ji-jf) <= lam <= ji+jf or lam not in (1,2,3,4):
        raise ValueError('Invalid photon angular momentum.')
    operators = emission_operators(ji,jf,lam)
    output = np.zeros((int(2*jf+1),int(2*jf+1)),complex)
    for helicity in (-1,1):
        coefficients = [np.exp(1j*q*phi)*small_d(lam,q,helicity,theta) for q in range(-lam,lam+1)]
        amplitude = np.einsum('q,qab->ab',coefficients,operators)
        output += amplitude@rho@amplitude.conj().T
    return output*(2*lam+1)/(8*pi)


def unobserved_map(density, ji, jf, lam):
    return sum(op@density@op.conj().T for op in emission_operators(ji,jf,lam))


def fold_detector(density, ji, jf, lam, theta_min, theta_max, phi_min=0., phi_max=2*pi,
                  efficiency=1., order=16):
    """Solid-angle fold in rest-frame orbit coordinates, Gauss–Legendre quadrature."""
    if not 0 <= theta_min < theta_max <= pi or not 0 <= phi_min < phi_max <= 2*pi or not 0 <= efficiency <= 1 or order < 4:
        raise ValueError('Invalid photon detector acceptance, efficiency or quadrature order.')
    # Integrate azimuth analytically: naive low-order Gauss quadrature over
    # 0..2pi aliases high multipole harmonics (notably E4).
    operators = emission_operators(ji,jf,lam)
    rho = np.asarray(density,complex)
    photon_map(rho,ji,jf,lam,0.,0.)  # validate density and angular momenta
    qs = np.arange(-lam,lam+1)
    kernel = np.array([[np.trace(left@rho@right.conj().T) for right in operators] for left in operators])
    delta = qs[:,None]-qs[None,:]
    azimuth = np.full(delta.shape,complex(phi_max-phi_min))
    mask = delta != 0
    azimuth[mask] = (np.exp(1j*delta[mask]*phi_max)-np.exp(1j*delta[mask]*phi_min))/(1j*delta[mask])
    nodes,weights = np.polynomial.legendre.leggauss(order)
    a,b = np.cos(theta_max),np.cos(theta_min)
    total = 0.
    for x,w in zip((a+b)/2+(b-a)/2*nodes,weights*(b-a)/2):
        for helicity in (-1,1):
            d = np.array([small_d(lam,int(q),helicity,np.arccos(x)) for q in qs])
            total += w*np.sum(kernel*azimuth*np.outer(d,d)).real
    return float(total*efficiency*(2*lam+1)/(8*pi))


def cascade_densities(reaction, densities, transitions):
    """Trace-preserving unobserved electric feeding; conversion needs isotropy.

    Conversion-electron feeding requires transfer coefficients unless rotational
    invariance fixes the result (isotropic parent or spin-zero daughter).
    """
    validate_network(reaction,transitions)
    if len(densities)!=len(reaction.levels):
        raise ValueError('Supply one spin density matrix per nuclear level.')
    output=[validate_density(rho,level.spin).copy() for rho,level in zip(densities,reaction.levels)]
    for upper in sorted(range(len(output)),key=lambda i:reaction.levels[i].energy,reverse=True):
        for edge in transitions:
            if edge.upper == upper and edge.branch:
                rho=output[upper];ji=reaction.levels[upper].spin;jf=reaction.levels[edge.lower].spin
                transfer=unobserved_map(rho,ji,jf,edge.multipolarity)
                if edge.alpha:
                    trace=float(np.trace(rho).real);size=len(rho)
                    scale=float(np.max(abs(rho)))
                    isotropic=np.eye(size)*trace/size
                    if jf!=0 and scale and not np.allclose(rho,isotropic,rtol=1e-10,atol=1e-13*scale):
                        raise ValueError('Aligned conversion feeding requires electron transfer tensors. An isotropic parent or spin-zero daughter is required without them.')
                    # Rotational invariance fixes the daughter of an unobserved
                    # isotropic parent, independently of electron partial waves; a spin-zero daughter is also unique.
                    transfer=np.eye(int(2*jf+1))*trace/(2*jf+1)
                output[edge.lower]+=edge.branch*transfer
    return output
