from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]


def test_research_modes_sensitivity_shapes_decay_and_staleness():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    app.number_input[ next(i for i,x in enumerate(app.number_input) if x.label=='Research angle samples') ].set_value(2).run()
    app.button(key='run_research_sensitivity').click().run()
    assert not app.exception and not app.error
    assert app.session_state['research_sensitivity'][1]['rows']
    app.number_input(key='beam_energy').set_value(68.).run()
    assert any('Research inputs changed' in v.value for v in app.info)
    app.selectbox(key='research_mode').set_value('Nuclear shape invariants').run()
    assert not app.exception
    app.selectbox(key='research_mode').set_value('Gamma cascades and correlations').run()
    app.button(key='run_research_decay').click().run()
    assert not app.exception and not app.error
    assert 'detected_photons' in app.session_state['research_decay'][1]
    app.selectbox(key='research_mode').set_value('Joint parameter fitting').run()
    assert not app.exception
    assert any('Download joint-fit JSON template' in d.label for d in app.get('download_button'))
    app.selectbox(key='research_mode').set_value('Octupole and model comparisons').run()
    assert not app.exception
    app.get_by_key('lang').set_value('el').run()
    assert not app.exception


def test_research_gaussian_ensemble_ui():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    app.selectbox(key='research_mode').set_value('Uncertainty bands').run()
    next(x for x in app.number_input if x.label=='Ensemble samples').set_value(10)
    next(x for x in app.number_input if x.label=='Research angle samples').set_value(2)
    app.button(key='run_research_uncertainty').click().run()
    assert not app.exception and not app.error
    assert len(app.session_state['research_uncertainty'][1]['draws'])==10


def test_single_parameter_profile_upload_and_plot():
    import json
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    app.selectbox(key='research_mode').set_value('Joint parameter fitting').run()
    config=dict(parameters=[dict(kind='element',index=1)],bounds=[[.1],[1.]],starts=[[.4]],
        experiments=[dict(kind='strength',data=[dict(level=1,lower=2,lam=2,value=.25,uncertainty=.02)])],
        profile=dict(parameter=1,grid=[.4,.5,.6]))
    next(x for x in app.file_uploader if x.label=='Upload joint-fit JSON').set_value(('profile.json',json.dumps(config).encode(),'application/json')).run()
    app.button(key='run_research_fit').click().run()
    assert not app.exception and not app.error
    fit=app.session_state['research_fit'][1]['fit']
    assert fit['success']
    assert len(fit['profile'])==3
    assert all(fit['profile'].success)
    assert any('Profile thresholds' in x.value for x in app.caption)
