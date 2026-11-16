"""Worked examples: using the `coulex` package from Python, without the web interface.

Run from the coulex_streamlit folder, with the environment created by run.py:

    .venv/bin/python examples/library_examples.py          (macOS/Linux)
    .venv\\Scripts\\python examples\\library_examples.py      (Windows)

Each function is independent and prints a short, labelled result.
"""
from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coulex import CoupledChannels, Level, MatrixElement, Reaction, SolverSettings, parse_input  # noqa: E402
from coulex.examples import BY_KEY  # noqa: E402
from coulex.literature import benchmark_suite, first_order_probability, rotor_matrix_element, rotor_q0_from_be2  # noqa: E402
from coulex.observables import integrate_detector, particle_yield  # noqa: E402
from coulex.stopping import StoppingTable  # noqa: E402
from coulex.workflow import calculate, results_frame  # noqa: E402


def example_1_single_angle():
    """Solve one collision of a built-in example and inspect the populations."""
    reaction = parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
    result = CoupledChannels(reaction).solve(90.)
    print('1) 22Mg + 104Pd at 90°: populations', np.round(result.probabilities, 5),
          f'(probability drift {result.norm_error:.1e})')


def example_2_angle_scan():
    """Angle scan with cross sections; results_frame gives a tidy table (also the app's CSV)."""
    example = BY_KEY['58Ni + 208Pb']
    reaction = example.reaction()
    scan = calculate(reaction, np.array([60., 120., 180.]))
    frame = results_frame(reaction, scan)
    excited = frame[frame.level == 2][['theta_cm_deg', 'probability', 'dsigma_cm_barn_per_sr']]
    print('2) 58Ni 2+ excitation (literature B(E2)):\n', excited.to_string(index=False))


def example_3_reaction_from_literature_numbers():
    """Build a reaction in code from a B(E2) value: <0||E2||2> = sqrt(B(E2; 0+ -> 2+))."""
    be2 = 3.4611                               # e² b², Pritychenko et al. (2016)
    q0 = rotor_q0_from_be2(be2)                # rigid rotor, Bohr & Mottelson
    levels = (Level(0., 0.), Level(2., 0.1217818), Level(4., 0.3664793))
    elements = (MatrixElement(0, 1, rotor_matrix_element(0, 2, q0)),
                MatrixElement(1, 1, rotor_matrix_element(2, 2, q0)),
                MatrixElement(1, 2, rotor_matrix_element(2, 4, q0)))
    reaction = Reaction('152Sm + 58Ni, three levels', 62, 152, 28, 58, 500., levels, elements)
    print('3) 152Sm (0+, 2+, 4+) at 150°:', np.round(CoupledChannels(reaction).solve(150.).probabilities, 4),
          '— with only three levels the top 4+ collects the flux; use the full band (built-in example) for physics')


def example_4_first_order_theory():
    """For a weak coupling the solver approaches Alder–Winther first-order theory."""
    base = parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
    weak = replace(base, dipole_strength=0., levels=base.levels[:2], elements=(MatrixElement(0, 1, 0.001, 2),))
    exact = CoupledChannels(weak).solve(120., SolverSettings(rtol=1e-11, atol=1e-15)).probabilities[1]
    print(f'4) weak E2 at 120°: coupled channels {exact:.6e}, first order {first_order_probability(weak, 120., 1):.6e}')


def example_5_detector_yield():
    """Counts in a 25°–55° lab annulus: integrate dσ/dΩ, then multiply by target atoms and beam."""
    reaction = parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
    angles = np.arange(20., 181., 5.)  # halve the step to check angular convergence
    scan = calculate(reaction, angles)
    level = 1
    sigma = integrate_detector(reaction, angles, scan.cross_sections[:, level], 25., 55., reaction.levels[level].energy)
    counts = particle_yield(sigma, reaction, thickness_mg_cm2=2., beam_per_second=1e5, days=5.)
    print(f'5) 2+ in a 25–55° annulus: σ = {sigma:.4g} b, {counts:.4g} particles in 5 days at 1e5/s')


def example_6_thick_target():
    """Average over the energy loss in a thick target with a stopping-power table."""
    reaction = parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
    table = StoppingTable.from_csv((ROOT/'examples/synthetic_stopping.csv').read_text())  # synthetic test data
    scan = calculate(reaction, np.array([90.]), stopping=table, thickness=2., order=6)
    print('6) thick target: beam energies sampled', np.round(scan.energies, 2), 'MeV; P(2+) =',
          round(float(scan.probabilities[0, 1]), 5))


def example_7_literature_benchmarks():
    """The same benchmarks as the app's Verification tab."""
    reference = parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
    rows = benchmark_suite(reference)
    print(f'7) literature benchmarks: {sum(r.passed for r in rows)} of {len(rows)} passed')
    for row in rows:
        print(f'   {"pass" if row.passed else "FAIL"}  {row.group}: {row.label} — difference {row.difference:.1e}')


if __name__ == '__main__':
    for function in (example_1_single_angle, example_2_angle_scan, example_3_reaction_from_literature_numbers,
                     example_4_first_order_theory, example_5_detector_yield, example_6_thick_target,
                     example_7_literature_benchmarks):
        function()
