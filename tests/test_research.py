"""Physics limits and statistical recovery, not implementation-mirroring tests."""
from dataclasses import replace
import json
import numpy as np
import pandas as pd
import pytest
from coulex.model import Reaction,Level,MatrixElement
from coulex.solver import CoupledChannels
from coulex.decay import (Transition,cascade,photon_map,fold_detector,unobserved_map,
                          electric_rate,cascade_densities,decay_rates)
from coulex.shapes import invariants
from coulex.literature import rotor_matrix_element
from coulex.research import (Parameter,sensitivity,ensemble,Experiment,joint_fit,likelihood_residual,
                              information_matrix,systematic_ensemble)
from coulex.workflow import calculate
from coulex.research_io import load_fit,fit_template


def rotor(q0=2.,top=4):
    spins=list(range(0,top+1,2))
    levels=tuple(Level(j,.02*j*(j+1)) for j in spins)
    elements=tuple(MatrixElement(i,j,rotor_matrix_element(a,b,q0)) for i,a in enumerate(spins) for j,b in enumerate(spins) if i<=j and abs(a-b)<=2 and a+b>=2)
    return Reaction('synthetic rotor',20,40,82,208,160.,levels,elements,dipole_strength=0.)


def test_shape_rotor_limit_and_phase_invariance():
    r=rotor(); v=invariants(r)
    assert v['q2']==pytest.approx(5/(16*np.pi)*4)
    assert v['cos3gamma']==pytest.approx(1.)
    assert v['q3']==pytest.approx(v['q2']**1.5)
    # Rephasing one basis state cannot change observable invariants.
    changed=replace(r,elements=tuple(replace(m,value=-m.value if (m.initial==1) != (m.final==1) else m.value) for m in r.elements))
    assert invariants(changed)['q3']==pytest.approx(v['q3'])
    oblate=invariants(rotor(-2.))
    assert oblate['cos3gamma']==pytest.approx(-1.)
    assert oblate['gamma_effective_deg']==pytest.approx(60.)
    incomplete=replace(r,elements=tuple(m for m in r.elements if m.initial!=m.final))
    assert invariants(incomplete)['missing_elements']


def test_gamma_cascade_conversion_and_feeding():
    r=rotor(); edges=(Transition(2,1,1.,1.),Transition(1,0,1.))
    occupancy,photons=cascade(r,[0,0,1],edges)
    assert photons==pytest.approx([.5,1.])
    assert occupancy==pytest.approx([1,1,1])
    with pytest.raises(ValueError): cascade(r,[0,0,1],(Transition(1,2,1),))
    with pytest.raises(ValueError): cascade(r,[0,0,1],(Transition(2,1,1.1),))
    with pytest.raises(ValueError): cascade_densities(r,[np.eye(1),np.eye(5),np.eye(9)],edges)


def test_radiation_analytic_patterns_and_solid_angle():
    # E1: |J=1,m=0> -> 0 has 3 sin²(theta)/(8pi).
    rho=np.diag([0.,1.,0.])
    for theta in (.2,.7,1.5):
        value=np.trace(photon_map(rho,1,0,1,theta,.3)).real
        assert value==pytest.approx(3*np.sin(theta)**2/(8*np.pi),rel=1e-12)
    # E2: |2,0> -> 0 gives 15 sin²(theta)cos²(theta)/(8pi).
    rho=np.diag([0.,0.,1.,0.,0.])
    for theta in (.2,.7,1.5):
        assert np.trace(photon_map(rho,2,0,2,theta,0.)).real==pytest.approx(15*np.sin(theta)**2*np.cos(theta)**2/(8*np.pi))
    assert fold_detector(rho,2,0,2,0,np.pi)==pytest.approx(1.,abs=1e-12)
    isotropic=np.eye(5)/5
    assert np.trace(photon_map(isotropic,2,0,2,.7,1.2)).real==pytest.approx(1/(4*np.pi))
    assert fold_detector(isotropic,2,0,2,np.pi/3,2*np.pi/3,efficiency=.4)==pytest.approx(.2)


def test_cascade_photon_correlation_and_trace():
    # 0 -> 1 -> 0 E1 cascade after first photon on z: W=3(1+cos²theta)/(16pi).
    daughter=photon_map(np.ones((1,1)),0,1,1,0.,0.)
    daughter/=np.trace(daughter)
    for theta in (.1,.8,2.):
        assert np.trace(photon_map(daughter,1,0,1,theta,0)).real==pytest.approx(3*(1+np.cos(theta)**2)/(16*np.pi))
    rng=np.random.default_rng(5); a=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5)); rho=a@a.conj().T; rho/=np.trace(rho)
    assert np.trace(unobserved_map(rho,2,2,2)).real==pytest.approx(1.)
    assert fold_detector(rho,2,2,2,0,np.pi,order=20)==pytest.approx(1.,abs=1e-12)
    # E4 has harmonics through 8phi; azimuth must be integrated exactly.
    a=rng.normal(size=(9,9))+1j*rng.normal(size=(9,9)); rho=a@a.conj().T; rho/=np.trace(rho)
    assert fold_detector(rho,4,0,4,0,np.pi,order=8)==pytest.approx(1.,abs=1e-12)


def test_electric_lifetime_rate_and_solver_density():
    assert electric_rate(1.,1e-4,2)==pytest.approx(1.2252e9,rel=2e-5)
    r=rotor(); result=CoupledChannels(r).solve(90)
    for population,rho in zip(result.probabilities,result.density_matrices):
        assert np.trace(rho).real==pytest.approx(population,abs=1e-14)
        assert np.linalg.eigvalsh(rho).min()>-1e-14
    assert decay_rates(r).total_branch.between(0,1).all()


def test_sensitivity_and_zero_uncertainty_ensemble():
    r=rotor(top=2); angles=[70.,120.]; parameter=Parameter('element',0)
    base,jac,error=sensitivity(r,angles,[parameter],[.001])
    h=.0001; direct=(calculate(parameter.set(r,parameter.get(r)+h),angles).cross_sections-calculate(parameter.set(r,parameter.get(r)-h),angles).cross_sections)/(2*h)
    assert jac[:,:,0]==pytest.approx(direct,rel=2e-5,abs=1e-9)
    draws,values,q=ensemble(r,angles,[parameter],[[0]],samples=10)
    assert q[0]==pytest.approx(base.cross_sections)
    assert q[-1]==pytest.approx(base.cross_sections)
    assert np.max(error)<1e-3
    with pytest.raises(ValueError): ensemble(r,angles,[parameter],[[-1]],samples=10)


def test_joint_fit_recovers_matrix_element_and_normalization():
    r=rotor(top=2); parameter=Parameter('element',0); truth=parameter.get(r)
    angles=[50.,100.,150.]
    data=pd.DataFrame(dict(angle_deg=angles,level=2,value=calculate(r,angles).cross_sections[:,1],uncertainty=.0001))
    # Use a second energy and a lifetime constraint in the same inference.
    second=r.at_energy(140.)
    data2=data.copy(); data2['value']=calculate(second,angles).cross_sections[:,1]
    life=decay_rates(r).lifetime_ps.iloc[0]
    constraints=Experiment(pd.DataFrame(dict(level=[2],value=[life],uncertainty=[life*.02])),kind='lifetime_ps')
    experiments=[Experiment(data,normalization_sigma=.05),Experiment(data2,energy_lab=140.),constraints]
    fit=joint_fit(parameter.set(r,truth*.8),[parameter],experiments,([.1],[2.]),starts=[[truth*.8],[truth*1.2]],max_nfev=20)
    assert fit['success']
    assert fit['values'][0]==pytest.approx(truth,rel=1e-5)
    assert fit['objective']<1e-8
    assert fit['covariance'] is not None


def test_likelihood_zero_counts_covariance_and_information():
    assert likelihood_residual([0,2],[1,2],'poisson')==pytest.approx([np.sqrt(2),0])
    with pytest.raises(ValueError): likelihood_residual([1.2],[2],'poisson')
    assert np.all(np.isfinite(likelihood_residual([1],[0],'poisson')))
    assert likelihood_residual([0,0],[1,2],'gaussian',covariance=[[1,0],[0,4]])==pytest.approx([1,1])
    info=information_matrix([[1],[1]],[1,1],normalization_prediction=[1,1])
    assert info[0,0]==pytest.approx(0,abs=1e-14)


def test_fit_template_roundtrip_and_cascade_prediction():
    r=rotor(); config,parameters,experiments=load_fit(fit_template(r))
    assert len(parameters)==1 and len(experiments)==1
    data=pd.DataFrame(dict(angle_min_deg=[60.],angle_max_deg=[65.],level=[2],value=[10.],efficiency=[1.],gamma_efficiency=[.1]))
    e=Experiment(data,kind='cascade_counts',frame='CM',transitions=(Transition(2,1,1.),Transition(1,0,1.)),photon_transition=1,angular_step=2.)
    assert e.predict(r)[0]>0


def test_external_constraints_profile_and_parameter_validation():
    from coulex.research import profile_fit
    from coulex.literature import spectroscopic_quadrupole
    from coulex.research_io import export_json
    r=rotor(top=2)
    p=[Parameter('element',0),Parameter('element',1)]
    strength=p[0].get(r)**2
    moment=spectroscopic_quadrupole(2,p[1].get(r))
    experiments=[Experiment(pd.DataFrame(dict(level=[1],lower=[2],lam=[2],value=[strength],uncertainty=[.01])),kind='strength'),
                 Experiment(pd.DataFrame(dict(level=[2],value=[moment],uncertainty=[.01])),kind='quadrupole')]
    truth=[x.get(r) for x in p]
    profile=profile_fit(r,p,experiments,([.1,-3.],[2.,3.]),0,[truth[0],truth[0]*1.05])
    assert profile.success.all()
    assert profile.objective.iloc[0]<1e-15
    assert profile.objective.iloc[1]>0
    assert json.loads(export_json({'value':np.nan}))=={'value':None}
    with pytest.raises(ValueError): Parameter('element',-1)
    with pytest.raises(ValueError): Experiment(experiments[0].data,kind='strength',reaction_overrides={'projectile_a':42}).predict(r)
