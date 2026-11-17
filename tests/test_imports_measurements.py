from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from coulex.imports import read_table, nuclear_tables, reaction_text, table_texts
from coulex.measurements import Exposure, validate_measurements, compare_measurements, cm_branches
from coulex import CoupledChannels, parse_input
from coulex.observables import rutherford, lab_angle, lab_jacobian, particle_yield
from coulex.stopping import StoppingTable

ROOT=Path(__file__).resolve().parents[1]


def test_nuclear_spreadsheet_roundtrip(magnesium):
    levels,elements=(read_table(text) for text in table_texts(magnesium))
    assert nuclear_tables(levels,elements)==(magnesium.levels,magnesium.elements)
    assert parse_input(reaction_text(magnesium))==magnesium
    assert nuclear_tables(levels.drop(columns='k'),elements)[0]==magnesium.levels  # k is optional


@pytest.mark.parametrize('text',[
    '\ufeffangle_deg;level;value;uncertainty\n90;2;0,23;0,01\n',
    'angle_deg\tlevel\tvalue\tuncertainty\n90\t2\t0.23\t0.01\n',
    'angle_deg,level,value,uncertainty\n90,2,0.23,0.01\n'])
def test_spreadsheet_delimiters(text):
    d=validate_measurements(read_table(text),'probability',3)
    assert d.value[0]==.23
    assert d.uncertainty[0]==.01


@pytest.mark.parametrize('text',['','a,a\n1,2','a,b\n1,2,3'])
def test_malformed_tables(text):
    with pytest.raises(ValueError): read_table(text)


def test_unknown_uncertainty_units_and_strict_integers():
    data=read_table('angle_deg,level,value,uncertainty\n90,2,120,\n')
    converted=validate_measurements(data,'cross_section',3,'mb/sr')
    assert converted.value[0]==.12
    assert np.isnan(converted.uncertainty[0])
    for change in [{'level':1.5},{'uncertainty':0},{'value':np.inf},{'angle_deg':0},{'level':4}]:
        bad=data.copy()
        for key,value in change.items(): bad[key]=value
        with pytest.raises(ValueError): validate_measurements(bad,'cross_section',3)
    assert validate_measurements(data,'cross_section',3,'fm²/sr').value[0]==1.2


def test_prediction_at_measured_angles_not_display_grid(magnesium):
    model=replace(magnesium,elements=())
    data=pd.DataFrame({'angle_deg':[43.21,96.43],'level':[1,1],'value':[0.,0.],'uncertainty':[.1,np.nan]})
    result=compare_measurements(model,data,'cross_section')
    np.testing.assert_allclose(result.predicted,rutherford(model,data.angle_deg),rtol=1e-12)
    assert result.standardized_residual[0]==pytest.approx(-result.predicted[0]/.1)
    assert np.isnan(result.standardized_residual[1])


def test_lab_cross_section_sums_both_branches(magnesium):
    model=replace(magnesium,projectile_a=104,projectile_z=46,target_a=22,target_z=12,energy_lab=300,elements=())
    branches=cm_branches(model,7,0)
    assert len(branches)==2
    expected=sum(rutherford(model,t)*lab_jacobian(model,np.array([t]))[0] for t in branches)
    data=pd.DataFrame({'angle_deg':[7,70],'level':[1,1],'value':[0,0]})
    actual=compare_measurements(model,data,'cross_section','Lab')
    assert actual.predicted[0]==pytest.approx(expected,rel=1e-12)
    assert actual.predicted[1]==0
    turning=np.rad2deg(np.arcsin(model.target_a/model.projectile_a))
    with pytest.raises(ValueError,match='turning-point'):
        cm_branches(model,turning,0)


@pytest.mark.parametrize('frame',['CM','Lab'])
def test_detector_counts_analytic_elastic_integral(magnesium,frame):
    model=replace(magnesium,elements=())
    lo,hi=(30.,80.) if frame=='CM' else lab_angle(model,np.array([30.,80.]))
    data=pd.DataFrame({'angle_min_deg':[lo],'angle_max_deg':[hi],'level':[1],'value':[100.],
                       'uncertainty':[10.],'efficiency':[.8]})
    exposure=Exposure(1e4,2.,1.,.5)
    coarse=compare_measurements(model,data,'particle_counts',frame,exposure=exposure,angular_step=2.)
    result=compare_measurements(model,data,'particle_counts',frame,exposure=exposure,angular_step=1.)
    exact_cs=4*np.pi*rutherford(model,180)*(1/np.tan(np.deg2rad(30)/2)**2-1/np.tan(np.deg2rad(80)/2)**2)*.5
    expected=particle_yield(exact_cs,model,1,1e4,2)*.8
    assert result.predicted[0]==pytest.approx(expected,rel=3e-5)
    assert abs(result.predicted[0]-expected)<abs(coarse.predicted[0]-expected)/4


def test_gamma_counts_apply_branch_and_efficiency(magnesium):
    data=pd.DataFrame({'angle_min_deg':[89.],'angle_max_deg':[91.],'level':[2],'value':[100.],
                      'efficiency':[.8],'branching_fraction':[.4],'gamma_efficiency':[.1]})
    particle=compare_measurements(magnesium,data,'particle_counts','CM',angular_step=1)
    gamma=compare_measurements(magnesium,data,'gamma_counts','CM',angular_step=1)
    assert gamma.predicted[0]==pytest.approx(particle.predicted[0]*.04)
    assert gamma.predicted[0]>0


def test_thick_target_measurement_uses_energy_dependent_cross_section(magnesium):
    model=replace(magnesium,elements=())
    data=pd.DataFrame({'angle_deg':[90.],'level':[1],'value':[0.]})
    stopping=StoppingTable(np.array([50.,80.]),np.array([2.,2.]))
    exposure=Exposure(thickness=2.)
    result=compare_measurements(model,data,'cross_section',stopping=stopping,exposure=exposure,order=4)
    _,energies,weights=stopping.quadrature(model.energy_lab,2.,4)
    assert result.predicted[0]==pytest.approx(sum(w*rutherford(model.at_energy(e),90.) for e,w in zip(energies,weights)))


def test_probability_and_invalid_count_inputs(magnesium):
    data=pd.DataFrame({'angle_deg':[90.],'level':[2],'value':[.23]})
    expected=CoupledChannels(magnesium).solve(90).probabilities[1]
    assert compare_measurements(magnesium,data,'probability').predicted[0]==pytest.approx(expected)
    with pytest.raises(ValueError,match='CM'):
        compare_measurements(magnesium,data,'probability','Lab')
    for filename in ('cross_section','probability','particle_counts','gamma_counts'):
        validate_measurements(read_table((ROOT/'examples/templates'/f'{filename}.csv').read_text(encoding='utf-8')),filename,3)
    with pytest.raises(ValueError): Exposure(thickness=-1)
    counts=read_table((ROOT/'examples/templates/particle_counts.csv').read_text(encoding='utf-8'))
    counts['efficiency']=90
    with pytest.raises(ValueError,match='efficiency'):
        validate_measurements(counts,'particle_counts',3)


def test_zero_angle_detector_rejected(magnesium):
    data=pd.DataFrame({'angle_min_deg':[0],'angle_max_deg':[10],'level':[1],'value':[10],'efficiency':[1]})
    with pytest.raises(ValueError,match='diverges'):
        compare_measurements(magnesium,data,'particle_counts','CM')
