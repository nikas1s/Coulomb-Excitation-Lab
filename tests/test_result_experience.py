"""User journeys: navigation, exact inspection, persistence and uncertainty displays."""
from pathlib import Path
import numpy as np
from streamlit.testing.v1 import AppTest
from coulex.plots import curves
from coulex.examples import EXAMPLES

ROOT = Path(__file__).resolve().parents[1]


def app():
    return AppTest.from_file(str(ROOT/'app.py'), default_timeout=120).run()


def test_run_opens_results_and_inspector_uses_computed_values():
    ui = app()
    ui.number_input(key='theta_min').set_value(80.)
    ui.number_input(key='theta_max').set_value(100.)
    ui.button(key='run_main').click().run()
    assert not ui.exception
    assert ui.session_state['work_tab'].endswith('Results')
    ui.select_slider(key='inspect_result_angle').set_value(100.).run()
    table = next(x.value for x in ui.dataframe if 'Population (%)' in x.value.columns)
    scan = ui.session_state['calculation']['scan']
    np.testing.assert_allclose(table['Population (%)'], 100*scan.probabilities[-1])
    np.testing.assert_allclose(table['dσ/dΩcm (barn/sr)'], scan.cross_sections[-1])
    ui.multiselect(key='plot_levels').set_value([]).run()
    assert not ui.exception
    assert any('Select at least one level' in x.value for x in ui.info)
    assert any(x.key=='download_results' for x in ui.get('download_button'))
    ui.get_by_key('lang').set_value('el').run()
    assert not ui.exception
    assert ui.session_state['work_tab'].endswith('Αποτελέσματα')
    assert ui.session_state['plot_levels']==[]
    assert ui.select_slider(key='inspect_result_angle').value==100.


def test_detector_results_survive_reruns_and_reject_stale_settings():
    ui = app()
    ui.number_input(key='theta_max').set_value(100.)
    ui.number_input(key='theta_step').set_value(40.)
    ui.button(key='run_main').click().run()
    ui.button(key='integrate').click().run()
    assert not ui.exception and 'detector_result' in ui.session_state
    stored = ui.session_state['detector_result'][1].copy()
    ui.checkbox(key='log_probability').check().run()
    assert any('detected particles' in x.value.columns for x in ui.dataframe)
    ui.get_by_key('lang').set_value('el').run()
    assert not ui.exception
    np.testing.assert_allclose(stored['detected particles'],ui.session_state['detector_result'][1]['detected particles'])
    ui.get_by_key('lang').set_value('en').run()
    ui.number_input(key='efficiency').set_value(.5).run()
    assert any('Detector settings changed' in x.value for x in ui.info)
    assert not any('detected particles' in x.value.columns for x in ui.dataframe)
    ui.button(key='integrate').click().run()
    np.testing.assert_allclose(ui.session_state['detector_result'][1]['detected particles'], .5*stored['detected particles'])


def test_uncertainty_view_excludes_unknown_uncertainties():
    ui=app()
    ui.file_uploader(key='measurement_file').set_value(('measurements.csv',
        b'angle_deg,level,value,uncertainty\n80,2,0.10,0.01\n90,2,0.12,\n','text/csv')).run()
    ui.button(key='compare').click().run()
    ui.checkbox(key='standardized_residuals').check().run()
    assert not ui.exception
    assert any('Only observations with uncertainties' in x.value for x in ui.caption)
    frame=ui.session_state['measurement_comparison'][1]
    assert np.isnan(frame.standardized_residual.iloc[1])
    ui.get_by_key('lang').set_value('el').run()
    assert not ui.exception
    assert ui.checkbox(key='standardized_residuals').value


def test_logarithmic_curves_do_not_change_or_connect_zero_values():
    reaction=EXAMPLES[0].reaction()
    values=np.zeros((3,len(reaction.levels)))
    values[:,1]=[.1,0,.2]
    before=values.copy()
    fig=curves(reaction,[30,60,90],values,'angle','probability',selected=[1],log=True)
    assert np.isnan(fig.data[0].y[1])
    assert fig.data[0].connectgaps is False
    np.testing.assert_array_equal(values,before)
