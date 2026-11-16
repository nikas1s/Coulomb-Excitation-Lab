from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]


def input_by_label(app,label):
    return next(x for x in app.number_input if x.label==label)


def button(app,label):
    return next(x for x in app.button if x.label==label)


def test_app_run_dynamics_export_and_stale_settings():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    assert not app.exception
    input_by_label(app,'Minimum CM angle (°)').set_value(90.)
    input_by_label(app,'Maximum CM angle (°)').set_value(90.)
    button(app,'Run calculation').click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state['calculation']['scan'].probabilities.shape==(1,3)
    button(app,'Follow the amplitudes').click().run()
    assert not app.exception
    assert app.session_state['dynamics'][1].history.shape==(3,401)
    input_by_label(app,'Beam energy (total MeV)').set_value(68.).run()
    assert any('Settings have changed' in x.value for x in app.info)
    assert not app.exception


def test_app_rejects_invalid_input():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    app.text_area[0].set_value('invalid').run()
    assert not app.exception
    assert any('Incomplete' in x.value or 'Invalid' in x.value for x in app.error)


def test_app_detector_and_example_switch():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    input_by_label(app,'Maximum CM angle (°)').set_value(100.)
    input_by_label(app,'Angle step (°)').set_value(40.)
    button(app,'Run calculation').click().run()
    assert not app.exception
    button(app,'Integrate detector yields').click().run()
    assert not app.exception
    assert not app.error
    assert any('detected particles' in x.value.columns for x in app.dataframe)
    next(x for x in app.selectbox if x.label=='Example').set_value('152Sm + 58Ni').run()
    assert not app.exception
    assert input_by_label(app,'Beam energy (total MeV)').value==500.


def by_label(widgets,label):
    return next(x for x in widgets if x.label==label)


def test_measurement_upload_mapping_units_and_stale_results():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    contents=b'theta,state,cross_section,error\n90,2,120,10\n'
    by_label(app.file_uploader,'Upload measurements (CSV or TSV)').set_value(('run.csv',contents,'text/csv')).run()
    by_label(app.selectbox,'Cross-section units').set_value('mb/sr').run()
    assert not app.exception
    assert not app.error
    button(app,'Compare measurements').click().run()
    assert not app.exception
    assert not app.error
    result=app.session_state['measurement_comparison'][1]
    assert result.value[0]==.12
    assert abs(result.predicted[0]-.0175572520)<1e-6  # default example: 22Mg + 104Pd, 2+ at 90° CM
    input_by_label(app,'Beam energy (total MeV)').set_value(68.).run()
    assert any('Measurement or reaction settings changed' in x.value for x in app.info)
    # Replace the bytes under the same filename: the new observation must be read.
    by_label(app.file_uploader,'Upload measurements (CSV or TSV)').set_value(('run.csv',b'theta,state,cross_section,error\n90,2,140,10\n','text/csv')).run()
    button(app,'Compare measurements').click().run()
    assert not app.exception
    assert app.session_state['measurement_comparison'][1].value[0]==.14


def test_spreadsheet_reaction_uploads_and_legacy_upload():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    by_label(app.radio,'Reaction source').set_value('My own tables').run()
    levels=b'level,spin,energy_mev,parity\n1,0,0,1\n2,2,1.5,1\n'
    elements=b'initial,final,value,lambda\n1,2,0.2,2\n'
    by_label(app.file_uploader,'Upload a CSV file (optional)').set_value(('levels.csv',levels,'text/csv'))
    app.file_uploader(key='matrix_elements_file').set_value(('elements.csv',elements,'text/csv')).run()
    for key,value in dict(table_zp=12,table_ap=22,table_zt=46,table_at=104).items():
        app.number_input(key=key).set_value(value)
    input_by_label(app,'Beam energy (total MeV)').set_value(67.)
    input_by_label(app,'Minimum CM angle (°)').set_value(90.)
    input_by_label(app,'Maximum CM angle (°)').set_value(90.)
    app.run()
    assert not app.exception
    assert not app.error
    button(app,'Run calculation').click().run()
    assert not app.exception
    assert app.session_state['calculation']['scan'].probabilities.shape==(1,2)
    by_label(app.radio,'Reaction source').set_value('My own reaction file').run()
    assert 'calculation' not in app.session_state  # results never carry over to another source
    text=b'new reaction\n1\n6 12\n20 40\n36\n30 90 10\n1 0 0 1 0\n'
    by_label(app.file_uploader,'Upload your reaction file').set_value(('custom.txt',text,'text/plain')).run()
    assert not app.exception
    assert not app.error
    assert input_by_label(app,'Beam energy (total MeV)').value==36.


def test_particle_count_upload_and_invalid_sigma():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    by_label(app.selectbox,'Measured observable').set_value('Detected particle counts').run()
    contents=b'angle_min_deg,angle_max_deg,level,value,uncertainty,efficiency\n89,91,2,1200,35,0.9\n'
    by_label(app.file_uploader,'Upload measurements (CSV or TSV)').set_value(('counts.csv',contents,'text/csv')).run()
    button(app,'Compare measurements').click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state['measurement_comparison'][1].predicted[0]>0
    contents=contents.replace(b'1200,35',b'1200,0')
    by_label(app.file_uploader,'Upload measurements (CSV or TSV)').set_value(('counts.csv',contents,'text/csv')).run()
    assert not app.exception
    assert any('Uncertainty must be' in x.value for x in app.error)
