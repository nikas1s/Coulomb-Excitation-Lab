from dataclasses import replace
import math
import numpy as np
import pandas as pd
import pytest
import mpmath as mp
from coulex import Reaction,Level,MatrixElement
from coulex.research import Experiment,Parameter,likelihood_residual,profile_fit
from coulex.acceptance import (recoil_lab_angle,recoil_jacobian,recoil_cm_roots,particle_intervals,
                               particle_energy,compare_particle_acceptance)


def model():
    return Reaction('acceptance test',38,96,50,120,275.5,(Level(0,0),Level(2,.815)),(MatrixElement(0,1,.5),),dipole_strength=0.)


def test_stable_poisson_residual_matches_high_precision():
    with mp.workdps(70):
        for n,delta in ((10**8,1),(10**12,-1),(10**12,1000),(10**12,2*10**9),(10**12,-2*10**9),(3,-2),(0,4)):
            mu=n+delta
            exact=mp.sign(delta)*mp.sqrt(2*(mu-n+(mp.mpf(n)*mp.log(mp.mpf(n)/mu) if n else 0)))
            value=likelihood_residual([n],[mu],'poisson')[0]
            assert value==pytest.approx(float(exact),rel=1e-12)
    assert likelihood_residual([0],[0],'poisson')[0]==0
    assert float(likelihood_residual(0,1,'poisson'))==pytest.approx(math.sqrt(2))
    with pytest.raises(ValueError,match='zero predicted mean'): likelihood_residual([1],[0],'poisson')


def test_single_parameter_profile_matches_exact_gaussian_and_nuisance_refit():
    r=model();p=Parameter('element',0)
    data=pd.DataFrame(dict(level=[1],lower=[2],lam=[2],value=[.25],uncertainty=[.02]))
    e=Experiment(data,kind='strength')
    grid=[.4,.5,.6]
    result=profile_fit(r,[p],[e],([.1],[1.]),0,grid)
    assert result.objective.to_numpy()==pytest.approx(((np.array(grid)**2-.25)/.02)**2)
    assert result.success.all()
    e.normalization_sigma=.1
    profiled=profile_fit(r,[p],[e],([.1],[1.]),0,grid)
    assert np.all(profiled.objective<=result.objective+1e-12)
    with pytest.raises(ValueError,match='inside'): profile_fit(r,[p],[e],([.1],[1.]),0,[2.])


def test_elastic_recoil_kinematics_and_jacobian():
    r=model(); theta=np.linspace(1,179,31)
    assert recoil_lab_angle(r,theta)==pytest.approx((180-theta)/2)
    assert recoil_jacobian(r,theta)==pytest.approx(4*np.sin(np.deg2rad(theta)/2),rel=1e-10)
    intervals=particle_intervals(r,20,55,detected_particle='recoil')
    assert np.asarray(intervals)==pytest.approx(np.array([[70.,140.]]))


def test_recoil_matches_two_body_momentum_and_conserves_energy():
    r=model();a,b=r.projectile_a,r.target_a;energy=.815
    momentum=np.sqrt(2*a*r.energy_lab);boost=momentum/(a+b)
    f=np.sqrt(1-energy/r.energy_cm);p=momentum*b/(a+b)*f
    for theta in (5.,60.,120.,175.):
        rad=np.deg2rad(theta)
        recoil=np.array([-p*np.sin(rad)/b,boost-p*np.cos(rad)/b])
        projectile=np.array([p*np.sin(rad)/a,boost+p*np.cos(rad)/a])
        angle=np.degrees(np.arctan2(abs(recoil[0]),recoil[1]))
        assert recoil_lab_angle(r,theta,energy)==pytest.approx(angle)
        assert particle_energy(r,theta,energy,'recoil')==pytest.approx(b*(recoil@recoil)/2)
        assert particle_energy(r,theta,energy,'projectile')==pytest.approx(a*(projectile@projectile)/2)
        assert b*(recoil@recoil)/2+a*(projectile@projectile)/2==pytest.approx(r.energy_lab-energy)


def test_inelastic_recoil_inverse_roots_and_threshold():
    r=model();energy=.815
    roots=recoil_cm_roots(r,30,energy)
    assert len(roots)==2
    assert recoil_lab_angle(r,np.array(roots),energy)==pytest.approx([30.,30.])
    intervals=particle_intervals(r,20,55,energy,'recoil')
    assert len(intervals)==2
    thresholded=particle_intervals(r,20,55,energy,'recoil',energy_min_mev=1.)
    assert len(thresholded)==1
    assert thresholded[0][0]>60


def test_particle_union_counts_overlap_once():
    r=model()
    projectile=particle_intervals(r,20,55,detected_particle='projectile')
    recoil=particle_intervals(r,20,55,detected_particle='recoil')
    union=particle_intervals(r,20,55,detected_particle='either')
    assert len(union)==1
    assert union[0][0]==pytest.approx(projectile[0][0])
    assert union[0][1]==pytest.approx(recoil[0][1])
    # The union covers the published high-CM region even though the scattered
    # projectile by itself cannot reach the entire region with this annulus.
    assert projectile[0][1]<103.8 and union[0][1]>139.


def test_recoil_count_prediction_matches_equivalent_cm_bin():
    from coulex.measurements import compare_measurements
    r=replace(model(),levels=(Level(0,0),Level(2,0)))
    data=pd.DataFrame(dict(angle_min_deg=[50.],angle_max_deg=[51.],level=[2],value=[10.],efficiency=[.8]))
    actual=compare_particle_acceptance(r,data,'particle_counts',frame='Lab',detected_particle='recoil')
    expected=data.copy();expected['angle_min_deg']=78.;expected['angle_max_deg']=80.
    reference=compare_measurements(r,expected,'particle_counts',frame='CM')
    assert actual.predicted.to_numpy()==pytest.approx(reference.predicted.to_numpy(),rel=1e-12)
    e=Experiment(data,kind='particle_counts',frame='Lab',detected_particle='recoil')
    assert e.predict(r)==pytest.approx(reference.predicted.to_numpy())


def test_impossible_poisson_profile_point_has_infinite_objective():
    from validation.research_qualification.nonlinear import setup,PopulationExperiment
    r,p,k=setup()
    e=PopulationExperiment(pd.DataFrame(dict(value=[2])),{},exposure=12.,likelihood='poisson')
    result=profile_fit(r,[p],[e],([0.],[math.pi/(2*k)]),0,[0.,p.get(r)])
    assert np.isinf(result.objective.iloc[0])
    assert result.success.iloc[0] and not result.compatible.iloc[0]
    assert np.isfinite(result.objective.iloc[1]) and result.compatible.iloc[1]
