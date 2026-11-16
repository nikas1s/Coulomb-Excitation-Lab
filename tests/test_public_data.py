"""Public level data: parsing rules, request safety and the own-tables interface (no network needed)."""
from pathlib import Path
import urllib.error
import urllib.request
import pytest
from streamlit.testing.v1 import AppTest
from coulex import public_data
from coulex.public_data import PublicDataError, fetch_levels_csv, nuclide_symbol, parse_levels

ROOT = Path(__file__).resolve().parents[1]
# Rows in the service's format (energies in keV), as returned for 22Mg; the ENSDF values are cited in the app.
SAMPLE = '''z,n,symbol,idx,energy_shift,energy,unc_e,jp,half_life,isospin
12,10,22MG,0,,0,,0+,3.8755,
12,10,22MG,1,,1247.02,0.03,2+,2.0,
12,10,22MG,2,,3308.22,0.06,4+,200,
12,10,22MG,3,,4402,0.3,2+,21,
12,10,22MG,4,,6242.7?,11,(6+),,
12,10,22MG,5,,,,(3+),,
12,10,22MG,6,,4500,1,"(2+,3)",,
12,10,22MG,7,,5296,0.4,(2-),,
'''


def test_nuclide_symbol_uses_service_notation():
    assert nuclide_symbol(12, 22) == '22Mg'
    assert nuclide_symbol(92, 238) == '238U'
    assert len(public_data.ELEMENTS) == 118


@pytest.mark.parametrize('z,a', [(0, 10), (119, 300), (12, 10), (12, 500)])
def test_impossible_nuclei_are_rejected(z, a):
    with pytest.raises(ValueError):
        nuclide_symbol(z, a)


def test_parse_levels_converts_units_and_keeps_only_certain_entries():
    loaded = parse_levels(SAMPLE, '22Mg', 5.0, '2026-11-16')
    levels = loaded.levels
    assert list(levels.energy_mev) == pytest.approx([0., 1.24702, 3.30822, 4.402])
    assert list(levels.spin) == [0., 2., 4., 2.]
    assert list(levels.parity) == [1, 1, 1, 1]
    assert list(levels.level) == [1, 2, 3, 4]
    # Uncertain or missing energies, and spins that are not unique, are listed rather than guessed.
    assert [code for _, code in loaded.skipped] == ['energy', 'energy', 'spin']
    assert loaded.retrieved == '2026-11-16'


def test_levels_above_the_energy_limit_are_not_loaded():
    loaded = parse_levels(SAMPLE, '22Mg', 3.5)
    assert list(loaded.levels.energy_mev) == pytest.approx([0., 1.24702, 3.30822])
    # Entries above the limit are not examined at all; only the two uncertain ones below it are listed.
    assert [code for _, code in loaded.skipped] == ['energy', 'energy']


def test_parity_and_fractional_spins():
    csv_text = 'z,n,symbol,idx,energy_shift,energy,unc_e,jp\n9,10,19F,0,,0,,3/2+\n9,10,19F,1,,110,,(5/2-)\n'
    levels = parse_levels(csv_text, '19F', 5.).levels
    assert list(levels.spin) == [1.5, 2.5] and list(levels.parity) == [1, -1]


def test_ground_state_is_required():
    with pytest.raises(PublicDataError, match='ground state'):
        parse_levels('z,n,symbol,idx,energy_shift,energy,unc_e,jp\n12,10,22MG,0,,1247,,2+\n', '22Mg', 5.)
    with pytest.raises(PublicDataError, match='no level data'):
        parse_levels('', '22Mg', 5.)


def test_invalid_names_never_reach_the_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('network used for an invalid name')
    monkeypatch.setattr(urllib.request, 'urlopen', forbidden)
    for name in ('22Mg&x=1', 'Mg22', '22Xx', '../22Mg', ''):
        with pytest.raises(PublicDataError):
            fetch_levels_csv(name)


def test_network_failure_is_reported_as_public_data_error(monkeypatch):
    def offline(*args, **kwargs):
        raise urllib.error.URLError('no route to host')
    monkeypatch.setattr(urllib.request, 'urlopen', offline)
    with pytest.raises(PublicDataError, match='no route to host'):
        fetch_levels_csv('22Mg')


def test_empty_service_answer_is_reported(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *exc): return False
        def read(self, size=-1): return b'2\n'
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: Response())
    with pytest.raises(PublicDataError, match='no level data for 22Mg'):
        fetch_levels_csv('22Mg')


def test_the_app_loads_levels_only_on_request(monkeypatch):
    calls = []

    def fake_download(nuclide):
        calls.append(nuclide)
        return SAMPLE
    monkeypatch.setattr(public_data, 'fetch_levels_csv', fake_download)
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=120).run()
    app.radio(key='reaction_source').set_value('My own tables').run()
    assert calls == []                                   # nothing requested just by opening the mode
    for key, value in (('table_zp', 12), ('table_ap', 22), ('table_zt', 82), ('table_at', 208)):
        app.number_input(key=key).set_value(value)
    app.run()
    assert calls == []
    app.button(key='load_levels').click().run()
    assert not app.exception
    assert calls == ['22Mg']                             # projectile is the default nucleus
    levels = [frame.value for frame in app.dataframe if frame.value.columns[0] == 'level'][0]
    assert list(levels['energy_mev'])[:3] == pytest.approx([0., 1.24702, 3.30822])
    assert app.session_state['public_levels'].nuclide == '22Mg'


def test_changing_the_nucleus_removes_levels_loaded_for_the_other_one(monkeypatch):
    monkeypatch.setattr(public_data, 'fetch_levels_csv', lambda nuclide: SAMPLE)
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=120).run()
    app.radio(key='reaction_source').set_value('My own tables').run()
    for key, value in (('table_zp', 12), ('table_ap', 22), ('table_zt', 82), ('table_at', 208)):
        app.number_input(key=key).set_value(value)
    app.run()
    app.button(key='load_levels').click().run()
    assert app.session_state['public_levels'].nuclide == '22Mg'
    app.number_input(key='table_ap').set_value(24).run()
    assert 'public_levels' not in app.session_state
