"""Regressions against archived numerical outputs, without source or a compiler.

The two TCLX inputs are not distributed (TCLX has no licence). Tests that need them are skipped
until they are downloaded into validation/tclx_inputs/ (see the README there).
"""
from pathlib import Path
from dataclasses import replace
import shutil
import numpy as np
import pytest
from coulex import CoupledChannels
from validation.verify import INPUTS, MissingComparisonInputs, load_inputs, load_reference

ROOT = Path(__file__).resolve().parents[1]
CASES = ['22Mg_104Pd_example', '80Sr_208Pb_example']
needs_inputs = pytest.mark.skipif(not all((INPUTS/f'{case}.txt').exists() for case in CASES),
                                  reason='TCLX inputs are not distributed; see validation/tclx_inputs/README.md')


def test_archived_reference_integrity():
    frame, manifest = load_reference()
    assert len(frame) == 2520
    assert manifest['polarization_convention'] == 'reference'
    assert manifest['angles'] == list(range(1, 181))
    assert sorted(manifest['examples_sha256']) == [f'{case}.txt' for case in CASES]


def test_changed_reference_is_rejected(tmp_path):
    archive = tmp_path/'validation/results'
    shutil.copytree(ROOT/'validation/results', archive)
    with (archive/'comparison.csv').open('a') as handle:
        handle.write('\nchanged reference\n')
    with pytest.raises(ValueError, match='Archived reference file changed: comparison.csv'):
        load_reference(tmp_path)


def test_missing_inputs_explain_where_to_get_them(tmp_path):
    _, manifest = load_reference()
    with pytest.raises(MissingComparisonInputs, match='github.com/jhenderson88/TCLX'):
        load_inputs(manifest, tmp_path)


def test_unlicensed_inputs_are_not_shipped_with_the_examples():
    assert not list((ROOT/'examples').glob('*_example.txt'))
    ignored = (ROOT/'.gitignore').read_text().split('\n')
    assert 'validation/tclx_inputs/*' in ignored and '!validation/tclx_inputs/README.md' in ignored


@needs_inputs
def test_changed_input_is_rejected(tmp_path):
    _, manifest = load_reference()
    for case in CASES:
        shutil.copy(INPUTS/f'{case}.txt', tmp_path)
    with (tmp_path/f'{CASES[0]}.txt').open('a') as handle:
        handle.write('\n# changed\n')
    with pytest.raises(ValueError, match=f'Comparison input changed: {CASES[0]}.txt'):
        load_inputs(manifest, tmp_path)


@needs_inputs
@pytest.mark.parametrize('example', CASES)
def test_against_archived_reference(example):
    frame, manifest = load_reference()
    model = replace(load_inputs(manifest)[example], polarization_convention='reference')
    solver = CoupledChannels(model)
    for angle in [1, 30, 90, 150, 180]:
        reference = frame[(frame.example == example) & (frame.theta_cm_deg == angle)].sort_values('level')
        assert len(reference) == len(model.levels)
        result = solver.solve(angle)
        np.testing.assert_allclose(result.probabilities, reference.original_probability, rtol=2e-5, atol=1e-6)
        assert result.norm_error < 1e-8
