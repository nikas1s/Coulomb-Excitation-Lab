"""Built-in examples: files in sync, cited data reproduced, highest-level population diagnostics."""
from dataclasses import replace
import numpy as np
import pytest
from coulex import CoupledChannels
from coulex.examples import BY_KEY, EXAMPLES, ROOT, SOURCES, TABLE_EXAMPLE
from coulex.imports import nuclear_tables, read_table, table_texts
from coulex.literature import AW60_TABLE5
from coulex.observables import surface_separation

LITERATURE = [e for e in EXAMPLES if e.kind == 'literature']


@pytest.mark.parametrize('example', EXAMPLES, ids=lambda e: e.key)
def test_example_files_are_in_sync_and_parse(example):
    assert (ROOT/'examples'/example.filename).read_text() == example.text()
    reaction = example.reaction()
    assert all(source in SOURCES for source in example.sources)
    assert all(datum.source in SOURCES for datum in example.data)
    assert reaction.levels[0].energy == 0


@pytest.mark.parametrize('example', LITERATURE, ids=lambda e: e.key)
def test_literature_examples_reproduce_cited_values(example):
    reaction = example.reaction()
    for datum in example.data:
        assert abs(datum.deviation(reaction)) <= 1, datum.quantity


def test_filled_table_examples_match_their_example_reaction():
    levels, elements = table_texts(BY_KEY[TABLE_EXAMPLE].reaction())
    assert (ROOT/'examples/templates/levels.csv').read_text() == levels
    assert (ROOT/'examples/templates/matrix_elements.csv').read_text() == elements
    reaction = BY_KEY[TABLE_EXAMPLE].reaction()
    assert nuclear_tables(read_table(levels), read_table(elements)) == (reaction.levels, reaction.elements)


def test_every_example_is_our_own_cited_input():
    assert {e.kind for e in EXAMPLES} <= {'literature', 'teaching'}
    assert all(example.generator for example in EXAMPLES)


@pytest.mark.parametrize('example', LITERATURE, ids=lambda e: e.key)
def test_literature_examples_have_surface_separation_and_small_top_population(example):
    reaction = replace(example.reaction(), excitation=example.excitation)
    assert surface_separation(reaction, np.array([180.]))[0] > 5
    if len(reaction.levels) > 2:
        top = max(CoupledChannels(reaction).solve(theta).probabilities[-1] for theta in (60., 120., 180.))
        assert top < 1e-3


def test_teaching_rotor_reproduces_aw60_table5():
    example = next(e for e in EXAMPLES if e.kind == 'teaching')
    assert not example.polarization  # the app switches the electric dipole polarization off for this model
    probabilities = CoupledChannels(replace(example.reaction(), dipole_strength=0.)).solve(180.).probabilities
    for spin, published in AW60_TABLE5[2.0].items():
        assert probabilities[spin//2] == pytest.approx(published, abs=1e-4)


def test_library_examples_script_runs(capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location('library_examples', ROOT/'examples/library_examples.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.example_1_single_angle()
    module.example_3_reaction_from_literature_numbers()
    module.example_4_first_order_theory()
    output = capsys.readouterr().out
    assert '1) 22Mg' in output and '4) weak E2' in output
