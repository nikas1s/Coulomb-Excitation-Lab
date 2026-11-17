"""Independent benchmark checks; no network or optional reference code required.

The statistical experiment below qualifies a regular, interior Gaussian case,
not coverage of arbitrary nonlinear Coulomb-excitation fits or small counts.
"""
from dataclasses import replace
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.stats import binomtest, norm
from coulex.model import Level, MatrixElement, Reaction
from coulex.decay import small_d, fold_detector, photon_map, unobserved_map
from coulex.shapes import invariants
from coulex.research import Experiment, Parameter, joint_fit

HERE=Path(__file__).resolve().parent


def published_shapes():
    fixture=json.loads((HERE/'cd106.json').read_text())
    r=Reaction('106Cd invariant benchmark',48,106,82,208,408.,
               tuple(Level(**x) for x in fixture['levels']),
               tuple(MatrixElement(**x) for x in fixture['elements']),dipole_strength=0.)
    actual=invariants(r)
    # Bound the difference due to rounding the independently printed inputs.
    # Sum absolute partial derivative bounds is less sharp; all 2^5 corners
    # suffice here because q2 is monotone and the q3 diagonal terms are affine
    # with fixed-sign derivatives over these narrow input intervals.
    corners=[]
    for signs in product((-1,1),repeat=len(r.elements)):
        local=replace(r,elements=tuple(replace(m,value=m.value+s*h) for m,s,h in zip(r.elements,signs,fixture['printed_half_steps'])))
        corners.append(invariants(local))
    checks={}
    for key,expected in fixture['published'].items():
        low=min(c[key] for c in corners)-fixture['published_half_steps'][key]
        high=max(c[key] for c in corners)+fixture['published_half_steps'][key]
        checks[key]=dict(calculated=actual[key],published=expected,rounding_envelope=[low,high],passed=bool(low<=expected<=high))
    return dict(source=fixture['source'],fixture_sha256=hashlib.sha256((HERE/'cd106.json').read_bytes()).hexdigest(),checks=checks,
                passed=all(x['passed'] for x in checks.values()),scope=fixture['scope'])


def angular_algebra():
    """Factorial Wigner d compared to a matrix exponential of spin Jy."""
    maximum=0.
    for j in range(1,5):
        m=np.arange(-j,j+1)
        raising=np.zeros((2*j+1,2*j+1),complex)
        for col,value in enumerate(m[:-1]):
            raising[col+1,col]=np.sqrt((j-value)*(j+value+1))
        jy=(raising-raising.conj().T)/(2j)
        for theta in (.13,.77,1.49,2.67):
            rotation=expm(-1j*theta*jy).real
            # Both references use ascending m and exp(-i theta Jy).
            reference=rotation
            actual=np.array([[small_d(j,int(a),int(b),theta) for b in m] for a in m])
            maximum=max(maximum,float(np.max(abs(actual-reference))))
    # Half-integer parents, all E1-E4, with coherent positive density matrices.
    rng=np.random.default_rng(151)
    normalization=0.; transfer=0.; isotropy=0.; cases=0
    for lam in range(1,5):
        for ji in (.5,1.,1.5,2.,3.,4.):
            for jf in (.5,1.,1.5,2.,3.,4.):
                if (ji-jf)%1 or not abs(ji-jf)<=lam<=ji+jf:
                    continue
                size=int(2*ji+1)
                a=rng.normal(size=(size,size))+1j*rng.normal(size=(size,size))
                rho=a@a.conj().T;rho/=np.trace(rho)
                transfer=max(transfer,float(abs(np.trace(unobserved_map(rho,ji,jf,lam))-1)))
                normalization=max(normalization,abs(fold_detector(rho,ji,jf,lam,0,np.pi,order=12)-1))
                value=np.trace(photon_map(np.eye(size)/size,ji,jf,lam,.83,.91)).real
                isotropy=max(isotropy,abs(value-1/(4*np.pi)))
                cases+=1
    return dict(cases=cases,wigner_d_max_error=maximum,normalization_max_error=normalization,
                transfer_max_error=transfer,isotropy_max_error=isotropy,
                passed=bool(maximum<1e-12 and max(normalization,transfer,isotropy)<1e-11))


def gaussian_coverage(trials=500,seed=581):
    """Independent exact Gaussian linear-Q estimation vs joint_fit's covariance.

    Each trial is fit through the real inference entry point using an external
    quadrupole constraint. Negative Q values and interior bounds are essential.
    """
    if trials<100:
        raise ValueError('Coverage qualification needs at least 100 trials.')
    r=Reaction('coverage reference',20,40,82,208,160.,(Level(0,0),Level(2,.3)),
               (MatrixElement(0,1,.5),MatrixElement(1,1,-.4)),dipole_strength=0.)
    p=Parameter('element',1); truth=p.get(r)
    # Independent Wigner–Eckart conversion (3j(2,2,2;-2,0,2)=sqrt(70)/35).
    coefficient=math.sqrt(16*np.pi/5)*math.sqrt(70)/35
    sigma=.04
    rng=np.random.default_rng(seed)
    hits={.68:0,.95:0};failed=0;estimator_error=0.;variance_error=0.
    estimates=[]
    for observation in rng.normal(coefficient*truth,sigma,trials):
        experiment=Experiment(pd.DataFrame(dict(level=[2],value=[observation],uncertainty=[sigma])),kind='quadrupole')
        fit=joint_fit(r,[p],[experiment],([-4.],[4.]),max_nfev=20)
        if not fit['success'] or fit['covariance'] is None:
            failed+=1;continue
        mean=fit['values'][0]; variance=fit['covariance'][0,0]
        estimator_error=max(estimator_error,abs(mean-observation/coefficient))
        variance_error=max(variance_error,abs(variance-(sigma/coefficient)**2))
        estimates.append(mean)
        for nominal in hits:
            radius=norm.ppf((1+nominal)/2)*np.sqrt(variance)
            hits[nominal]+=bool(abs(mean-truth)<=radius)
    intervals={}
    for nominal,hit in hits.items():
        ci=binomtest(hit,trials).proportion_ci(confidence_level=.99,method='exact')
        intervals[str(nominal)]=dict(hits=int(hit),trials=trials,observed=hit/trials,
                binomial_99_interval=[ci.low,ci.high],passed=bool(ci.low<=nominal<=ci.high))
    return dict(trials=trials,seed=seed,failed=failed,intervals=intervals,
                estimator_max_error=estimator_error,variance_max_error=variance_error,
                mean_estimate=float(np.mean(estimates)),truth=truth,
                passed=bool(not failed and estimator_error<1e-7 and variance_error<1e-8 and all(v['passed'] for v in intervals.values())),
                scope='Interior linear Gaussian external-Q constraints only; not nonlinear/Poisson/normalization coverage')


def gosia_replay():
    """Replay only finite reference cases; unusable reference runs stay explicit."""
    path=HERE/'gosia_points/results.json'
    reference=json.loads(path.read_text())
    rows=[];unusable=[];cache={}
    from coulex.solver import CoupledChannels,SolverSettings
    for row in reference['rows']:
        if not row.get('reference_valid',True):
            unusable.append(dict(case=row['case'],reason=row['reason']))
            continue
        data=dict(row['model'])
        data['levels']=tuple(Level(**x) for x in data['levels'])
        data['elements']=tuple(MatrixElement(**x) for x in data['elements'])
        key=(row['case'],row['cm_angle'])
        if key not in cache:
            cache[key]=CoupledChannels(Reaction(**data)).solve(row['cm_angle'],SolverSettings(rtol=1e-11,atol=1e-14,extra_omega=1.)).probabilities
        actual=float(cache[key][row['level']-1])
        difference=abs(actual-row['reference'])
        rows.append(dict(case=row['case'],level=row['level'],cm_angle=row['cm_angle'],
                    expected=row['reference'],actual=actual,absolute_difference=difference,
                    passed=bool(difference<=1e-10+3e-4*abs(row['reference']))))
    return dict(source_url=reference['source_url'],source_sha256=reference['source_sha256'],
                reference_fixture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                compared_points=len(rows),rows=rows,unusable_reference_cases=unusable,
                passed=bool(rows and all(r['passed'] for r in rows)),
                scope='Finite GOSIA cases only: target E2/E3 populations, E2 multistep/reorientation and unpolarized half-integer spins, polarization off. E1/E4 reference runs were nonfinite and do not qualify those multipoles.')


def experimental_inputs():
    folder=HERE/'experiments/sr96_sn120'
    manifest=json.loads((folder/'manifest.json').read_text())
    data=pd.read_csv(folder/'yields.csv')
    missing=[key for key,value in manifest['required_inputs'].items() if value is None]
    valid=bool(len(data)==7 and data.value.notna().all() and (data.uncertainty>0).all()
               and (data.angle_max_deg>data.angle_min_deg).all())
    return dict(source=manifest['doi'],data_integrity_passed=valid,observation_count=len(data),
                missing_inputs=missing,ready_for_experimental_validation=bool(valid and not missing),
                data_sha256=hashlib.sha256((folder/'yields.csv').read_bytes()).hexdigest(),
                scope='Bibliographic experimental target selected; no experimental fit is claimed')
