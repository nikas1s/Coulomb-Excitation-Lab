from dataclasses import replace
import numpy as np
import pytest
from scipy.integrate import quad
from coulex import Level, MatrixElement, CoupledChannels, parse_input
from coulex.model import angle_grid
from coulex.observables import (rutherford,lab_angle,lab_jacobian,detector_cm_intervals,
                                integrate_detector,particle_yield,surface_separation)
from coulex.stopping import StoppingTable
from coulex.workflow import calculate
from coulex.solver import collision_functions


def test_e4_correct_real_division_coefficient():
    assert collision_functions(4,1,0)[0].real == pytest.approx(35/64)


def test_zero_coupling_and_ground_state(magnesium):
    r=CoupledChannels(replace(magnesium,elements=())).solve(90,history_points=21)
    np.testing.assert_array_equal(r.probabilities,[1,0,0])
    np.testing.assert_array_equal(r.history.sum(axis=0),np.ones(21))


def test_degenerate_two_channel_analytic_solution(magnesium):
    model=replace(magnesium,levels=(Level(0.,0.),Level(2.,0.)),
                  elements=(MatrixElement(0,1,.5,2),),dipole_strength=0.)
    solver=CoupledChannels(model)
    result=solver.solve(180)
    # Only m=0 couples on the head-on orbit; H(ω) commutes with H(ω').
    # An independent scalar quadrature gives the exact two-channel rotation.
    area=quad(lambda w:solver.hamiltonian(w,1)[3,0].real,-result.endpoint,result.endpoint,
              epsabs=1e-12,epsrel=1e-12)[0]
    np.testing.assert_allclose(result.probabilities,[np.cos(area)**2,np.sin(area)**2],atol=1e-10)


@pytest.mark.parametrize('lam',[1,2,3,4])
def test_electric_multipoles_are_hermitian_and_conserve_probability(magnesium,lam):
    model=replace(magnesium,levels=(Level(0.,0.),Level(float(lam),.4,(-1)**lam)),
                  elements=(MatrixElement(0,1,.1,lam),))
    solver=CoupledChannels(model)
    for omega in (-1.,0.,.5):
        h=solver.hamiltonian(omega,1.7)
        np.testing.assert_allclose(h,h.conj().T,atol=1e-13)
    result=solver.solve(90)
    assert result.norm_error < 1e-8
    assert result.probabilities[1]>0


def test_unpolarized_half_integer_ground_state(magnesium):
    model=replace(magnesium,levels=(Level(.5,0.),Level(1.5,.5)),elements=(MatrixElement(0,1,.1,2),))
    solver=CoupledChannels(model)
    assert solver.ground_size==2
    h=solver.hamiltonian(.4,1.7)
    np.testing.assert_allclose(h,h.conj().T,atol=1e-14)
    r=solver.solve(90)
    assert abs(sum(r.probabilities)-1)<1e-9
    # Reflection symmetry of an initially unpolarized beam.
    np.testing.assert_allclose(r.substate_probabilities[:2],r.substate_probabilities[:2][::-1],atol=1e-10)


def test_all_negative_couplings_are_not_discarded(magnesium):
    positive=replace(magnesium,levels=magnesium.levels[:2],elements=(MatrixElement(0,1,.1,2),))
    negative=replace(positive,elements=(MatrixElement(0,1,-.1,2),))
    a=CoupledChannels(positive).solve(60).probabilities
    b=CoupledChannels(negative).solve(60).probabilities
    assert a[1]>.0001
    np.testing.assert_allclose(a,b,atol=1e-12)


def test_target_excitation_preserves_relative_motion(magnesium):
    target=replace(magnesium,excitation='target')
    swapped=replace(magnesium,projectile_z=magnesium.target_z,projectile_a=magnesium.target_a,
                    target_z=magnesium.projectile_z,target_a=magnesium.projectile_a,
                    energy_lab=magnesium.energy_lab*magnesium.target_a/magnesium.projectile_a)
    assert target.energy_cm==pytest.approx(swapped.energy_cm)
    np.testing.assert_allclose(CoupledChannels(target).hamiltonian(.3,2),
                               CoupledChannels(swapped).hamiltonian(.3,2),rtol=1e-13,atol=1e-13)


def test_rutherford_units_and_analytic_annulus(magnesium):
    model=magnesium
    angles=np.linspace(30,100,701)
    cs=rutherford(model,angles)
    assert rutherford(model,180)==pytest.approx((model.head_on_distance/4)**2/100)
    bounds=lab_angle(model,np.array([30.,100.]))
    numerical=integrate_detector(model,angles,cs,*bounds)
    exact=4*np.pi*rutherford(model,180)*(1/np.tan(np.deg2rad(30)/2)**2-1/np.tan(np.deg2rad(100)/2)**2)
    assert numerical==pytest.approx(exact,rel=2e-8)
    assert particle_yield(1,model,2,1e5,5)==pytest.approx(1e-24*(.002/104*6.02214076e23)*1e5*432000)


def test_lab_jacobian_by_finite_difference(magnesium):
    theta=np.deg2rad(70.)
    step=1e-6
    phi=np.deg2rad(lab_angle(magnesium,70.,1.247))
    derivative=(np.deg2rad(lab_angle(magnesium,np.rad2deg(theta+step),1.247))-
                np.deg2rad(lab_angle(magnesium,np.rad2deg(theta-step),1.247)))/(2*step)
    expected=np.sin(theta)/np.sin(phi)/abs(derivative)
    assert lab_jacobian(magnesium,np.array([70.]),1.247)[0]==pytest.approx(expected,rel=1e-9)


def test_inverse_kinematics_has_both_detector_branches(magnesium):
    model=replace(magnesium,projectile_a=104,projectile_z=46,target_a=22,target_z=12,energy_lab=300)
    intervals=detector_cm_intervals(model,5,10)
    assert len(intervals)==2
    for a,b in intervals:
        assert 5<lab_angle(model,(a+b)/2)<10
    # Constant isotropic cross section has exact solid-angle integrals.
    expected=sum(2*np.pi*(np.cos(np.deg2rad(a))-np.cos(np.deg2rad(b))) for a,b in intervals)
    angles=np.linspace(.1,180,1800)
    assert integrate_detector(model,angles,np.ones_like(angles),5,10)==pytest.approx(expected,rel=1e-10)
    assert detector_cm_intervals(model,50,70)==[]


def test_detector_requires_complete_angular_coverage(magnesium):
    with pytest.raises(ValueError,match='extend'):
        integrate_detector(magnesium,np.array([40,80]),np.ones(2),10,60)
    with pytest.raises(ValueError,match='at least two'):
        integrate_detector(magnesium,np.array([90]),np.ones(1),25,55)


def test_stopping_constant_solution_and_quadrature():
    table=StoppingTable(np.array([1.,100.]),np.array([2.,2.]))
    depth,energy=table.profile(67,3)
    np.testing.assert_allclose(energy,67-2*depth,atol=1e-11)
    x,e,w=table.quadrature(67,3)
    np.testing.assert_allclose(e,67-2*x,atol=1e-10)
    assert sum(w)==pytest.approx(1)
    assert np.dot(w,e)==pytest.approx(64)
    with pytest.raises(ValueError,match='exits'):
        table.profile(10,10)
    with pytest.raises(ValueError,match='inside'):
        table.profile(101,1)


def test_thick_target_averages_cross_sections_at_each_energy(magnesium):
    model=replace(magnesium,elements=())
    table=StoppingTable(np.array([1.,100.]),np.array([1.,1.]))
    result=calculate(model,[90.],stopping=table,thickness=2.,order=4)
    expected=sum(w*rutherford(model.at_energy(e),90) for e,w in zip(result.energies,result.weights))
    assert result.cross_sections[0,0]==pytest.approx(expected)
    np.testing.assert_array_equal(result.probabilities,[[1,0,0]])


def test_surface_radius_uses_cube_root(magnesium):
    expected=magnesium.head_on_distance-1.25*(22**(1/3)+104**(1/3))
    assert surface_separation(magnesium,180)==pytest.approx(expected)


def test_angle_grid_includes_endpoint_and_single_angle():
    np.testing.assert_array_equal(angle_grid(1,10,4),[1,5,9,10])
    np.testing.assert_array_equal(angle_grid(90,90,1),[90])
    for args in [(0,90,1),(90,10,1),(1,180,0),(1,180,float('nan'))]:
        with pytest.raises(ValueError): angle_grid(*args)


@pytest.mark.parametrize('mutation',[
    {'energy_lab':float('nan')}, {'energy_lab':1.}, {'theta_step':-1.},
    {'levels':(Level(.1,0),)}, {'levels':(Level(0,1),)},
    {'elements':(MatrixElement(0,1,.2,5),)}, {'elements':(MatrixElement(0,1,.2,1),)},
    {'elements':(MatrixElement(0,8,.2,2),)},
    {'elements':(MatrixElement(0,1,.2,2),MatrixElement(1,0,.2,2))},
])
def test_invalid_models_rejected(magnesium,mutation):
    with pytest.raises(ValueError): replace(magnesium,**mutation)


def test_malformed_input_and_single_angle_legacy_notation():
    with pytest.raises(ValueError): parse_input('bad input')
    text='one level\n1\n12 22\n46 104\n67\n90 0 0\n1 0 0 1 0\n'
    model=parse_input(text)
    assert model.theta_max==90
    assert model.theta_step==1
