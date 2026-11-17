"""Kumar–Cline q2/q3 sums for 0+ states, in e² b² and e³ b³.

q3 = -sqrt(7/10) Σ <0||E2||2i><2i||E2||2j><2j||E2||0>.
Only the supplied space enters: missing elements are zero, not measured zeros.
"""
import numpy as np
from .research import apply_parameters, covariance_matrix


def reduced(reaction, a, b, lam=2):
    for me in reaction.elements:
        if me.multipolarity == lam:
            if (me.initial, me.final) == (a,b):
                return me.value
            if (me.initial, me.final) == (b,a):
                return (-1)**int(reaction.levels[a].spin-reaction.levels[b].spin)*me.value
    return 0.


def invariants(reaction, state=0, radius_fm=None):
    level = reaction.levels[state]
    if level.spin != 0 or level.parity != 1:
        raise ValueError('This invariant implementation requires a 0+ state.')
    twos = [i for i,x in enumerate(reaction.levels) if x.spin == 2 and x.parity == 1]
    vector = np.array([reduced(reaction,state,i) for i in twos])
    matrix = np.array([[reduced(reaction,i,j) for j in twos] for i in twos]).reshape(len(twos),len(twos))
    q2 = float(vector@vector)
    q3 = float(-np.sqrt(7/10)*(vector@matrix@vector))
    ratio = q3/q2**1.5 if q2 > 0 else np.nan
    gamma = float(np.degrees(np.arccos(ratio))/3) if np.isfinite(ratio) and abs(ratio) <= 1 else np.nan
    z,a,*_ = reaction.effective_nuclei
    radius = 1.2*a**(1/3) if radius_fm is None else radius_fm
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError('Charge radius convention must be positive.')
    # sqrt(q2) in eb -> e fm². Sharp-surface small-deformation mapping.
    beta = 4*np.pi*100*np.sqrt(q2)/(3*z*radius**2)
    keys = {(min(m.initial,m.final),max(m.initial,m.final)) for m in reaction.elements if m.multipolarity==2}
    needed = {(min(state,i),max(state,i)) for i in twos}
    needed |= {(min(i,j),max(i,j)) for i in twos for j in twos if reduced(reaction,state,i) and reduced(reaction,state,j)}
    return dict(q2=q2, q3=q3, cos3gamma=ratio, gamma_effective_deg=gamma, beta_effective=float(beta),
                radius_fm=radius, two_plus_levels=[i+1 for i in twos], missing_elements=sorted(needed-keys),
                contributions=[dict(level=i+1, q2=float(v*v)) for i,v in zip(twos,vector)])


def invariant_ensemble(reaction, parameters, covariance, samples=1000, seed=2026, state=0):
    if not isinstance(samples,int) or not 10 <= samples <= 100000:
        raise ValueError('Use 10–100000 invariant ensemble samples.')
    covariance = covariance_matrix(covariance,len(parameters))
    draws = np.random.default_rng(seed).multivariate_normal([p.get(reaction) for p in parameters],covariance,samples)
    return [invariants(apply_parameters(reaction,parameters,draw),state) for draw in draws]
