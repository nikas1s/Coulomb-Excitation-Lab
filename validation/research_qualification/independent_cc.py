"""Independent geometric Coulomb Hamiltonian with unitary midpoint propagation.

Uses spherical harmonics of the actual Rutherford separation vector and the
Wigner–Eckart theorem. It does not import production collision polynomials,
operators, coupling constants or ODE routines. CODATA 2018 constants are used.
The finite orbit and midpoint discretization must be independently converged.
"""
import math
import numpy as np
from scipy.special import sph_harm_y
from sympy import Rational
from sympy.physics.wigner import wigner_3j

ALPHA=7.2973525693e-3
HBARC=197.3269804
AMU=931.49410242


def geometric_midpoint(reaction,angle,steps=8000,endpoint=10.):
    if not 0<angle<=180 or not isinstance(steps,int) or steps<100 or not 2<=endpoint<=20:
        raise ValueError('Invalid independent propagation grid.')
    if reaction.dipole_strength:
        raise ValueError('The independent geometric benchmark currently excludes effective polarization.')
    # Physical reduced masses and level-dependent relative velocities.
    zp,ap,zt,at,_=reaction.effective_nuclei
    mass=AMU*ap*at/(ap+at)
    energy=reaction.energy_cm-np.array([x.energy for x in reaction.levels])
    beta=np.sqrt(2*energy/mass)
    eta=zp*zt*ALPHA/beta
    states=[(i,float(m)) for i,l in enumerate(reaction.levels) for m in np.arange(-l.spin,l.spin+1)]
    size=len(states);ground=int(2*reaction.levels[0].spin+1)
    e_sub=np.array([eta[i]-eta[0] for i,m in states])
    operators={}
    for me in reaction.elements:
        if not me.value: continue
        lam=me.multipolarity
        # Stored ME has its first index as the bra. Hermitian reversal is exact.
        pairs=[(me.final,me.initial,me.value)]
        if me.initial!=me.final:
            phase=(-1)**int(reaction.levels[me.initial].spin-reaction.levels[me.final].spin)
            pairs.append((me.initial,me.final,phase*me.value))
        for source,dest,value in pairs:
            ji,jf=reaction.levels[source].spin,reaction.levels[dest].spin
            speed=math.sqrt(beta[source]*beta[dest])
            a=zp*zt*ALPHA*HBARC/(2*math.sqrt(energy[source]*energy[dest]))
            scale=zt*ALPHA/speed/a**lam*(4*math.pi/(2*lam+1))*10**lam*value
            for row,(level_f,mf) in enumerate(states):
                if level_f!=dest: continue
                for col,(level_i,mi) in enumerate(states):
                    if level_i!=source: continue
                    mu=int(round(mf-mi))
                    if abs(mu)>lam: continue
                    args=[jf,lam,ji,-mf,mu,mi]
                    symbol=float(wigner_3j(*(Rational(round(2*x),2) for x in args)))
                    matrix=operators.setdefault((lam,mu),np.zeros((size,size),complex))
                    matrix[row,col]+=(-1)**int(round(jf-mf))*symbol*scale
    amplitude=np.zeros((size,ground),complex);amplitude[:ground]=np.eye(ground)
    epsilon=1/math.sin(math.radians(angle)/2)
    step=2*endpoint/steps
    hermitian_error=0.
    for omega in -endpoint+(np.arange(steps)+.5)*step:
        b=epsilon*np.cosh(omega)+1
        z=(np.cosh(omega)+epsilon)/b
        polar=math.acos(float(np.clip(z,-1.,1.)))
        azimuth=math.copysign(math.pi/2,omega)
        h=np.zeros((size,size),complex)
        for (lam,mu),matrix in operators.items():
            h+=matrix*sph_harm_y(lam,mu,polar,azimuth).conjugate()/b**lam
        phase=np.exp(1j*e_sub*(epsilon*np.sinh(omega)+omega))
        h=phase[:,None]*h*phase.conj()[None,:]
        hermitian_error=max(hermitian_error,float(np.max(abs(h-h.conj().T))))
        if hermitian_error>1e-12:
            raise RuntimeError('The independently constructed Hamiltonian is not Hermitian.')
        eigenvalues,eigenvectors=np.linalg.eigh(h)
        amplitude=eigenvectors@(np.exp(-1j*step*eigenvalues)[:,None]*(eigenvectors.conj().T@amplitude))
    substate=np.mean(abs(amplitude)**2,axis=1)
    probabilities=np.bincount([i for i,m in states],weights=substate,minlength=len(reaction.levels))
    densities=tuple(amplitude[[n for n,(level,m) in enumerate(states) if level==i]]@amplitude[[n for n,(level,m) in enumerate(states) if level==i]].conj().T/ground for i in range(len(reaction.levels)))
    return dict(probabilities=probabilities,density_matrices=densities,norm_error=float(np.max(abs(np.sum(abs(amplitude)**2,axis=0)-1))),
                hermitian_error=hermitian_error,steps=steps,endpoint=endpoint)
