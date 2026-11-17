"""Independent reference checks, including adversarial scientific inputs."""
import numpy as np
import pandas as pd
import pytest
from validation.research_qualification.checks import published_shapes,angular_algebra,gosia_replay
from coulex.research import covariance_matrix,Experiment
from coulex.decay import decay_rates
from coulex import Reaction,Level


def test_published_cd106_invariants_from_printed_matrix_elements():
    assert published_shapes()['passed']


def test_rotation_exponential_and_photon_trace_over_spins():
    result=angular_algebra()
    assert result['cases']==60
    assert result['passed']


def test_independent_gosia_finite_reference_points():
    result=gosia_replay()
    assert result['compared_points']==15
    assert result['passed']
    # Unusable reference calculations are retained, not relabelled as passes.
    assert {row['case'] for row in result['unusable_reference_cases']}=={'E1 isolated','E4 isolated'}


def test_covariance_validation_is_independent_of_unit_scale():
    with pytest.raises(ValueError):
        covariance_matrix([[1e-20,1e-15],[0,1e-20]],2)
    for scale in (1e-25,1.,1e25):
        assert covariance_matrix(scale*np.array([[1.,.3],[.3,2.]]),2)==pytest.approx(scale*np.array([[1.,.3],[.3,2.]]))
    with pytest.raises(ValueError): covariance_matrix(np.empty((0,0)),0)
    with pytest.raises(ValueError): covariance_matrix([[1e20,1e5],[0,1e-20]],2)
    with pytest.raises(ValueError): covariance_matrix([[1e20,2.],[2.,1e-20]],2)
    with pytest.raises(ValueError): covariance_matrix([[1e20,0],[0,-1e-20]],2)
    assert covariance_matrix([[1e20,.3],[.3,1e-20]],2).shape == (2,2)


def test_missing_lifetime_rates_give_scientific_input_error():
    r=Reaction('no specified decays',8,16,28,58,60.,(Level(0,0),Level(2,1.)),())
    assert decay_rates(r).empty
    with pytest.raises(ValueError,match='outgoing decay rate'):
        Experiment(pd.DataFrame(dict(level=[2],value=[1.],uncertainty=[.1])),kind='lifetime_ps').predict(r)


def test_experimental_fixture_is_not_presented_as_a_validated_fit():
    from validation.research_qualification.checks import experimental_inputs
    report=experimental_inputs()
    assert report['data_integrity_passed']
    assert report['observation_count']==7
    assert not report['ready_for_experimental_validation']
    assert 'gamma_response' in report['missing_inputs']


def test_independent_gosia_extended_cases():
    result=gosia_replay('gosia_expanded/results.json')
    assert result['compared_points']==12
    assert not result['unusable_reference_cases']
    assert result['passed']
