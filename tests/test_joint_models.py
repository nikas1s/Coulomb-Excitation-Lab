"""Target-normalized inference and independent calibration-prior bookkeeping."""
from dataclasses import asdict,replace
import json
import numpy as np
import pandas as pd
import pytest
from coulex import Reaction,Level,MatrixElement
from coulex.joint_model import JointModel,configured_model
from coulex.research import Parameter,Experiment,joint_fit,apply_parameters,_fit_objective,fit_predictions
from coulex.research_io import load_fit


def models():
    primary=Reaction('projectile',8,16,28,58,30.,(Level(0,0),Level(2,.2)),
                     (MatrixElement(0,1,.4),),excitation='projectile',dipole_strength=0.)
    target=replace(primary,title='target',excitation='target',levels=(Level(0,0),Level(2,.3)),
                   elements=(MatrixElement(0,1,.3),))
    return primary,target


def test_simultaneous_projectile_target_fit_recovers_shared_free_normalization():
    primary,target=models();bundle=JointModel({'primary':primary,'target':target})
    parameters=[Parameter('element',0),Parameter('element',0,'target')]
    experiments=[];scale=1.25
    for name in ('primary','target'):
        data=pd.DataFrame(dict(angle_deg=[70.,120.],level=[2,2],value=[0.,0.],uncertainty=[1.,1.]))
        e=Experiment(data,model=name,normalization_group='same_beam')
        data['value']=scale*e.predict(bundle);data['uncertainty']=.03*data.value
        experiments.append(e)
    experiments.append(Experiment(pd.DataFrame(dict(level=[1],lower=[2],lam=[2],
        value=[.3**2],uncertainty=[.003])),kind='strength',model='target'))
    fit=joint_fit(bundle,parameters,experiments,([.1,.1],[.8,.8]),starts=[[.35,.35]],max_nfev=30)
    assert fit['success'] and fit['covariance'] is not None
    assert fit['values']==pytest.approx([.4,.3,np.log(scale)],rel=2e-5)
    assert fit['objective']<1e-8
    assert fit['normalization_groups']==[dict(name='same_beam',experiments=[0,1],prior_sigma=None)]
    predictions=fit_predictions(bundle,parameters,experiments,fit)
    assert predictions[0]['normalization_scale']==pytest.approx(scale,rel=2e-5)
    for entry in predictions:
        for row in entry['data']: assert row['predicted']==pytest.approx(row['value'],rel=2e-5)
    changed=parameters[1].set(bundle,.2)
    assert changed.selected().elements[0].value==.4
    assert changed.selected('target').elements[0].value==.2
    assert bundle.selected('target').elements[0].value==.3


def test_shared_prior_is_counted_once_and_conflicts_are_rejected():
    primary,_=models()
    data=pd.DataFrame(dict(level=[1],lower=[2],lam=[2],value=[.4**2],uncertainty=[.02]))
    experiments=[Experiment(data,kind='strength',normalization_group='calibration',normalization_sigma=.1) for _ in range(2)]
    residual,representatives,groups=_fit_objective(primary,[],experiments,None)
    eta=.03;expected=(eta/.1)**2+2*((np.exp(eta)-1)*.4**2/.02)**2
    assert residual([eta])@residual([eta])==pytest.approx(expected)
    assert representatives==[0] and len(groups)==1
    experiments[1].normalization_sigma=.2
    with pytest.raises(ValueError,match='conflicting'): _fit_objective(primary,[],experiments,None)
    with pytest.raises(ValueError,match='distinct'): apply_parameters(primary,[Parameter('element',0),Parameter('element',0,'primary')],[.3,.4])


def test_portable_named_models_and_lab_response_configuration():
    primary,target=models()
    definition=asdict(target)
    for element in definition['elements']:
        element['initial']+=1;element['final']+=1
    config=dict(models={'target':definition},parameters=[dict(kind='element',index=1,model='target')],
        experiments=[dict(kind='angular_gamma_counts',model='target',normalization_group='beam',
            transitions=[dict(upper=2,lower=1,branch=1.)],photon_transition=1,
            gamma_response=dict(detectors=[dict(theta_min_deg=30.,theta_max_deg=60.,efficiency=.4)]),
            data=[dict(angle_min_deg=60.,angle_max_deg=62.,level=2,value=4.,uncertainty=2.,efficiency=1.)])])
    parsed,parameters,experiments=load_fit(json.dumps(config));bundle=configured_model(parsed,primary)
    assert parameters[0].get(bundle)==.3
    assert experiments[0].model=='target'
    assert experiments[0].gamma_response.detectors[0].weights_sr.sum()>0
    with pytest.raises(ValueError,match='unknown'): bundle.selected('missing')
    with pytest.raises(ValueError): configured_model({'models':{'primary':asdict(target)}},primary)
    with pytest.raises(ValueError): Parameter('element',0,'')


def test_plot_residuals_follow_correlated_gaussian_normalization_convention():
    primary,_=models()
    gaussian=Experiment(pd.DataFrame(dict(level=[1,1],lower=[2,2],lam=[2,2],value=[.14,.19])),
        kind='strength',covariance=[[.001,.0002],[.0002,.002]],normalization_sigma=.1)
    # An external Gaussian test with a known scale exercises covariance whitening.
    fit=dict(values=np.array([.4,.03]),normalization_groups=[dict(experiments=[0],prior_sigma=.1)])
    entry=fit_predictions(primary,[Parameter('element',0)],[gaussian],fit)[0]
    expected=np.linalg.solve(np.linalg.cholesky(gaussian.covariance),np.full(2,.4**2*np.exp(.03))-[.14,.19])
    assert [row['likelihood_residual'] for row in entry['data']]==pytest.approx(expected)
    assert entry['correlated']
