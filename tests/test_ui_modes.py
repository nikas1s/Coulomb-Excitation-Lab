"""Examples stay examples; own-data modes start empty; Greek interface; in-app help."""
from pathlib import Path
from streamlit.testing.v1 import AppTest
from coulex.examples import EXAMPLES
from coulex.formats import FORMATS
from coulex.i18n_el import EL
from i18n_strings import dynamic_strings, literal_t_calls

ROOT = Path(__file__).resolve().parents[1]


def start():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=120).run()
    assert not app.exception
    return app


def test_every_interface_string_has_a_greek_translation():
    missing = sorted((literal_t_calls() | dynamic_strings()) - set(EL))
    assert not missing, missing


def test_own_file_mode_never_uses_example_data_or_results():
    app = start()
    app.button(key='run').click().run()
    assert 'calculation' in app.session_state
    app.radio(key='reaction_source').set_value('My own reaction file').run()
    assert not app.exception
    assert 'calculation' not in app.session_state
    assert app.session_state['beam_energy'] is None
    assert app.button(key='run').disabled
    assert any('Upload your reaction file' in w.value for w in app.warning)
    # No example level scheme is shown for an empty own-data source.
    assert not app.get('plotly_chart')


def test_own_tables_start_empty():
    app = start()
    app.radio(key='reaction_source').set_value('My own tables').run()
    assert not app.exception
    editors = [frame for frame in app.dataframe if frame.value.columns[0] in ('level', 'initial')]
    assert editors and all(frame.value.empty for frame in editors)
    for key in ('table_zp', 'table_ap', 'table_zt', 'table_at', 'beam_energy'):
        assert app.session_state[key] is None
    assert app.button(key='run').disabled


def test_switching_examples_discards_previous_results_and_sets_defaults():
    app = start()
    app.button(key='run').click().run()
    app.selectbox(key='example').set_value('16O + 238U').run()
    assert not app.exception
    assert 'calculation' not in app.session_state
    assert app.session_state['excitation'] == 'target'
    assert app.session_state['beam_energy'] == 66.


def test_greek_interface_runs_and_keeps_inputs():
    app = start()
    app.number_input(key='beam_energy').set_value(68.).run()
    app.get_by_key('lang').set_value('el').run()
    assert not app.exception
    assert app.session_state['reaction_source'] == 'example'
    assert app.session_state['excitation'] == 'projectile'
    assert app.title[0].value == 'Εργαστήριο Διέγερσης Coulomb'
    assert app.session_state['beam_energy'] == 68.
    app.button(key='run').click().run()
    assert not app.exception
    assert 'calculation' in app.session_state
    labels = [b.label for b in app.button]
    assert 'Εκτέλεση υπολογισμού' in labels
    # A translated choice survives a language switch (Streamlit stores it by its label).
    app.radio(key='reaction_source').set_value('Δικοί μου πίνακες').run()
    app.get_by_key('lang').set_value('en').run()
    assert not app.exception
    assert app.session_state['reaction_source'] == 'tables'
    app.radio(key='reaction_source').set_value('Built-in example').run()
    app.get_by_key('lang').set_value('el').run()
    # Library errors are shown in Greek.
    app.text_area[0].set_value('invalid').run()
    assert any('Ελλιπής είσοδος αντίδρασης' in e.value for e in app.error)


def test_instructions_and_formats_are_in_the_app():
    app = start()
    markdown = '\n'.join(m.value for m in app.markdown)
    assert 'What this app does' in markdown and 'Calculate your own reaction' in markdown
    for fmt in FORMATS.values():
        assert fmt.purpose in markdown
    downloads = [b for b in app.get('download_button')]
    assert len(downloads) >= 2*len(FORMATS)


def test_every_example_loads():
    app = start()
    for example in EXAMPLES:
        app.selectbox(key='example').set_value(example.key).run()
        assert not app.exception, example.key
        assert not app.error, example.key
        assert not app.button(key='run').disabled


def test_start_screen_is_the_calculation_and_help_is_separate():
    app = start()
    labels = [tab.label for tab in app.tabs]
    position = {label.split(' ', 1)[1]: i for i, label in enumerate(labels)}
    assert labels[0].endswith('Calculation')  # opened first
    assert position['Measurements'] < position['Help and reference'] < position['Guide']
    assert position['Help and reference'] < min(position['Physics'], position['Verification'], position['File formats'])
    calculation, help_section = app.tabs[0], app.tabs[position['Help and reference']]
    calculation_text = '\n'.join(m.value for m in calculation.markdown)
    help_text = '\n'.join(m.value for m in help_section.markdown)
    assert 'What this app does' in help_text and 'What this app does' not in calculation_text
    assert 'From a level scheme to a detector count' in help_text  # physics
    assert 'Benchmarks against published theory' not in '\n'.join(h.value for h in calculation.header)
