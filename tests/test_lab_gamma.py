from dataclasses import replace
import math
import numpy as np
import pytest
from coulex import Reaction,Level
from coulex.decay import photon_map,validate_density,cascade_densities,Transition
from coulex.lab_gamma import (GammaMesh,orbit_to_lab,emitter_beta,inverse_photon_boost,
                             angular_kernel,angular_density,fold_lab_gamma)


def reaction(lam=2,excitation='projectile'):
    return Reaction('lab response',8,16,28,58,30.,(Level(0,0),Level(lam,.3,(-1)**lam)),(),excitation=excitation,dipole_strength=0.)


def test_rotation_matches_incoming_and_outgoing_rutherford_velocities():
    for theta in (.2,1.3,2.8):
        c,s=np.cos(theta/2),np.sin(theta/2)
        incoming=np.array([0,c,-s]);outgoing=np.array([0,c,s])
        for phi in (.0,.7):
            for excited,sign in [('projectile',1),('target',-1)]:
                matrix=orbit_to_lab(theta,phi,excited)
                assert matrix.T@matrix==pytest.approx(np.eye(3),abs=1e-14)
                assert np.linalg.det(matrix)==pytest.approx(1.)
                assert matrix@incoming==pytest.approx([0,0,sign],abs=1e-14)
                expected=sign*np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
                assert matrix@outgoing==pytest.approx(expected,abs=1e-14)


def test_vectorized_radiation_equals_direct_photon_operator():
    rng=np.random.default_rng(55)
    for lam in (1,2,3,4):
        size=2*lam+1;a=rng.normal(size=(size,size))+1j*rng.normal(size=(size,size));rho=a@a.conj().T;rho/=np.trace(rho)
        mesh=GammaMesh.annulus(10,170,order=4,phi_order=9)
        actual=angular_density(angular_kernel(rho,lam,0,lam),lam,mesh.directions)
        expected=[np.trace(photon_map(rho,lam,0,lam,np.arccos(n[2]),np.arctan2(n[1],n[0]))).real for n in mesh.directions]
        assert actual==pytest.approx(expected,rel=1e-12,abs=1e-14)


def test_lorentz_aberration_and_isotropic_lab_density():
    b=.2
    lab=np.array([[0,0,1.],[0,0,-1.],[1.,0,0.]])
    rest,doppler=inverse_photon_boost(lab,[0,0,b])
    assert np.linalg.norm(rest,axis=1)==pytest.approx(np.ones(3))
    assert rest[:,2]==pytest.approx([1.,-1.,-b])
    gamma=1/np.sqrt(1-b*b)
    assert doppler==pytest.approx(1/(gamma*(1-b*lab[:,2])))
    assert doppler[0]==pytest.approx(np.sqrt((1+b)/(1-b)))


def test_full_solid_angle_preserves_photon_number_with_boost_and_alignment():
    rng=np.random.default_rng(7)
    for lam in (1,2,4):
        r=reaction(lam);n=2*lam+1;a=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n));rho=a@a.conj().T;rho/=np.trace(rho)
        mesh=GammaMesh.annulus(0,180,order=20,phi_order=40)
        for excited in ('projectile','target'):
            local=replace(r,excitation=excited)
            actual=fold_lab_gamma(local,1.2,rho,1,0,lam,mesh,particle_phi=.7)
            assert actual==pytest.approx(1.,abs=2e-10)
        assert fold_lab_gamma(r,1.2,rho,1,0,lam,mesh,boost=False)==pytest.approx(1.,abs=1e-12)


def test_intrinsic_efficiency_and_calibration_extrapolation():
    r=reaction();rho=np.eye(5)/5
    detector=GammaMesh.annulus(60,120,efficiency=.4)
    assert fold_lab_gamma(r,1.,rho,1,0,2,detector,boost=False)==pytest.approx(.2)
    curve=GammaMesh.annulus(0,180,energy_mev=[.299,.301],efficiency_curve=[.5,.5])
    with pytest.raises(ValueError,match='calibration range'): fold_lab_gamma(r,1.,rho,1,0,2,curve)
    valid=GammaMesh.annulus(0,180,energy_mev=[.2,.4],efficiency_curve=[.5,.5])
    assert fold_lab_gamma(r,1.,rho,1,0,2,valid)==pytest.approx(.5,abs=1e-10)


def test_density_validation_is_relative_and_conversion_isotropy_is_exact():
    for scale in (1.,1e-40):
        with pytest.raises(ValueError): validate_density(scale*np.array([[1.,.2],[0.,1.]]),.5)
        with pytest.raises(ValueError): validate_density(scale*np.diag([1.,-.1]),.5)
    r=Reaction('isotropic conversion feed',8,16,28,58,30.,(Level(0,0),Level(2,.1),Level(0,.4)),())
    edges=(Transition(2,1,.7,2.),Transition(1,0,1.,.1))
    density=[np.zeros((1,1)),np.zeros((5,5)),np.ones((1,1))]
    result=cascade_densities(r,density,edges)
    assert result[1]==pytest.approx(np.eye(5)*.7/5)
    assert result[0][0,0]==pytest.approx(.7)
    # A forbidden aligned conversion transfer is irrelevant for a zero branch.
    r=Reaction('zero branch',8,16,28,58,30.,(Level(0,0),Level(2,.1),Level(4,.4)),())
    densities=[np.zeros((1,1)),np.zeros((5,5)),np.diag([1.]+[0.]*8)]
    assert not np.any(cascade_densities(r,densities,(Transition(2,1,0.,1.),))[1])


def test_gamma_mesh_rejects_invalid_weights_efficiencies_and_angles():
    from coulex.gamma_yields import GammaResponse
    with pytest.raises(ValueError): GammaMesh([[0,0,1]],[-1.],[1.])
    with pytest.raises(ValueError): GammaMesh([[0,0,1]],[1.],[1.2])
    with pytest.raises(ValueError): GammaMesh.from_csv('theta_deg,phi_deg,weight_sr,intrinsic_efficiency\n200,0,1,.5\n')
    with pytest.raises(ValueError): GammaResponse((GammaMesh.annulus(0,180),),boost='false')
    with pytest.raises(ValueError): emitter_beta(reaction(),float('nan'),.3)


def test_oriented_m_zero_radiation_matches_independent_legendre_formula():
    # |L,0> -> |0,0>: W = (2L+1)(1-c²)[P'_L(c)]²/[4pi L(L+1)].
    # This checks rotation signs, boost Jacobian and sector integration without
    # using photon operators or Wigner rotations as the expected calculation.
    from numpy.polynomial import Legendre
    mesh=GammaMesh.annulus(25.,130.,phi_min_deg=20.,phi_max_deg=150.,efficiency=.7,order=10,phi_order=15)
    for lam in (1,2,3,4):
        rho=np.zeros((2*lam+1,2*lam+1));rho[lam,lam]=1.
        for excited in ('projectile','target'):
            r=reaction(lam,excited);theta=1.1;phi=.8
            axis=orbit_to_lab(theta,phi,excited)[:,2]
            rest,doppler=inverse_photon_boost(mesh.directions,emitter_beta(r,theta,.3,phi))
            c=rest@axis
            expected=(2*lam+1)/(4*np.pi*lam*(lam+1))*(1-c*c)*Legendre.basis(lam).deriv()(c)**2
            expected=np.sum(expected*doppler**2*mesh.weights_sr*.7)
            actual=fold_lab_gamma(r,theta,rho,1,0,lam,mesh,particle_phi=phi)
            assert actual==pytest.approx(expected,rel=1e-12,abs=1e-14)


def test_laboratory_full_sphere_counts_match_population_cascade_limit():
    import pandas as pd
    from coulex import MatrixElement
    from coulex.gamma_yields import GammaResponse
    from coulex.research import Experiment
    r=Reaction('gamma yield limit',8,16,28,58,30.,(Level(0,0),Level(2,.1),Level(0,.4)),
        (MatrixElement(0,1,.3),MatrixElement(1,1,-.1),MatrixElement(1,2,.3)),dipole_strength=0.)
    edges=(Transition(2,1,.7,1.),Transition(1,0,1.,.1))
    data=pd.DataFrame(dict(angle_min_deg=[80.],angle_max_deg=[82.],level=[2],value=[100.],efficiency=[.8],gamma_efficiency=[.1]))
    isotropic=Experiment(data,kind='cascade_counts',transitions=edges,photon_transition=1)
    reference=isotropic.predict(r)
    data=data.copy();data['gamma_efficiency']=1.
    response=GammaResponse((GammaMesh.annulus(0,180,efficiency=.1,order=12,phi_order=24),),particle_phi_order=4)
    lab=Experiment(data,kind='angular_gamma_counts',transitions=edges,photon_transition=1,gamma_response=response)
    actual=lab.predict(r)
    assert actual==pytest.approx(reference,rel=2e-6)
    data['gamma_efficiency']=.1
    with pytest.raises(ValueError,match='twice'): lab.predict(r)
