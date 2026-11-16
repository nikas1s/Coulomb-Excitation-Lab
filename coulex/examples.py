"""Built-in example reactions, each with documented provenance.

Examples are *only* starting points: the app never mixes them into a user's own
reaction. Two kinds exist:

* ``literature`` — level energies, B(Eλ) values and quadrupole moments taken
  from evaluated nuclear data, cited per number. Higher band members of
  rotational nuclei use rigid-rotor matrix elements (marked as model values).
* ``teaching`` — an exactly solvable model whose answer is tabulated in the
  literature (Alder & Winther 1960, Table 5).

Examples are generated here in Python so that the cited numbers and the derived
matrix elements live in one place; ``write_example_files`` exports them to
``examples/`` and a test keeps the files in sync. The TCLX example inputs used
for the archived code comparison are not distributed (TCLX has no licence); see
``validation/tclx_inputs/README.md``.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from .literature import (REFERENCES as THEORY, aw60_q, diagonal_from_quadrupole, rotor_matrix_element,
                         rotor_q0_from_be2, spectroscopic_quadrupole)
from .imports import table_texts
from .model import Level, Reaction, parse_input

ROOT = Path(__file__).resolve().parents[1]

DATA_SOURCES = {
    'PR16': 'B. Pritychenko, M. Birch, B. Singh, M. Horoi, "Tables of E2 transition probabilities from the '
            'first 2+ states in even–even nuclei", [At. Data Nucl. Data Tables 107, 1 (2016)](https://arxiv.org/abs/1312.5975), Table 3',
    'NDS22': 'M. Shamsuzzoha Basunia, [Nucl. Data Sheets 127, 69 (2015)](https://www.nndc.bnl.gov/ensnds/22/Mg/adopted.pdf) — ENSDF, A = 22',
    'NDS58': 'C. D. Nesaraja, S. D. Geraedts, B. Singh, [Nucl. Data Sheets 111, 897 (2010)](https://www.nndc.bnl.gov/ensnds/58/Ni/adopted.pdf) — ENSDF, A = 58',
    'NDS152': 'M. J. Martin, [Nucl. Data Sheets 114, 1497 (2013)](https://www.nndc.bnl.gov/ensnds/152/Sm/adopted.pdf) — ENSDF, A = 152',
    'NDS208': 'M. J. Martin, [Nucl. Data Sheets 108, 1583 (2007)](https://www.nndc.bnl.gov/ensnds/208/Pb/adopted.pdf) — ENSDF, A = 208',
    'NDS238': 'E. Browne, J. K. Tuli, [Nucl. Data Sheets 127, 191 (2015)](https://www.nndc.bnl.gov/ensnds/238/U/adopted.pdf) — ENSDF, A = 238',
}
SOURCES = {**THEORY, **DATA_SOURCES}


def _element(reaction, initial, final, lam):
    for me in reaction.elements:
        if {me.initial, me.final} == {initial, final} and me.multipolarity == lam:
            return me.value
    return 0.


def b_up(initial, final, lam):
    """B(Eλ; initial → final) implied by the input, e² b^λ."""
    return lambda r: _element(r, initial, final, lam)**2/(2*r.levels[initial].spin+1)


def q_spectroscopic(level):
    """Spectroscopic quadrupole moment implied by the diagonal E2 element, e b."""
    return lambda r: spectroscopic_quadrupole(r.levels[level].spin, _element(r, level, level, 2))


def level_energy(level):
    return lambda r: r.levels[level].energy


@dataclass(frozen=True)
class Datum:
    """One literature number and the value implied by the example input."""
    quantity: str
    literature: float
    minus: float
    plus: float
    unit: str
    source: str
    implied: Callable[[Reaction], float]
    model: bool = False   # True: the input uses a model value, compared with experiment

    def deviation(self, reaction):
        """Signed deviation of the input value in units of the literature uncertainty."""
        delta = self.implied(reaction)-self.literature
        sigma = self.plus if delta > 0 else self.minus
        return delta/sigma if sigma > 0 else float('inf') if delta else 0.


@dataclass(frozen=True)
class Example:
    key: str
    kind: str                 # 'literature' | 'teaching'
    filename: str
    excitation: str
    summary: str              # English; translated in the UI
    focus: str                # English; translated in the UI
    sources: tuple[str, ...]
    angles: tuple[float, float, float] = (20., 180., 10.)
    data: tuple[Datum, ...] = ()
    polarization: bool = True   # default of the electric dipole-polarization switch
    generator: Callable[[], str] | None = field(default=None, repr=False)

    def text(self):
        return self.generator() if self.generator else (ROOT/'examples'/self.filename).read_text()

    def reaction(self):
        return parse_input(self.text())


def tclx_text(comments, title, projectile, target, energy, angles, levels, elements):
    """Write reaction text with citation comments."""
    lines = [f'# {line}' if line else '#' for line in comments]
    lines += [title, str(len(levels)), f'{projectile[0]} {projectile[1]}', f'{target[0]} {target[1]}',
              f'{energy:g}', '{:g} {:g} {:g}'.format(*angles)]
    lines += [f'{i+1} {spin:g} {e:.10g} {parity} 0' for i, (spin, e, parity) in enumerate(levels)]
    lines += [f'{i} {f} {value:.10f} {lam}' for i, f, value, lam in elements]
    return '\n'.join(lines)+'\n'


def _rotor_elements(spins, q0):
    elements = []
    for i, spin in enumerate(spins):
        if spin:
            elements.append((i+1, i+1, rotor_matrix_element(spin, spin, q0), 2))
        if i+1 < len(spins):
            elements.append((i+1, i+2, rotor_matrix_element(spin, spins[i+1], q0), 2))
    return elements


def _magnesium():
    be2 = 0.034
    q0 = rotor_q0_from_be2(be2)
    return tclx_text([
        '22Mg radioactive beam on 104Pd: a light nucleus whose B(E2) is known only to about 40%.',
        'E(2+) = 1247.02 keV, E(4+) = 3308.22 keV [M. S. Basunia, NDS 127, 69 (2015)]',
        'B(E2; 0+ -> 2+) = 0.034(+16-11) e2 b2 [Pritychenko et al., ADNDT 107, 1 (2016)]',
        f'<2||E2||4> from the rigid-rotor model with Q0 = sqrt(16pi B/5) = {q0:.4f} e b (model value).',
        'Q(2+) is not measured, so no diagonal (reorientation) element is included; add a "2 2 value 2" line',
        'to explore its effect.',
        '66 MeV = 3.0 MeV/u keeps the nuclear surfaces > 5 fm apart at every angle.',
    ], '22Mg + 104Pd, 66 MeV (literature data + rigid rotor)', (12, 22), (46, 104), 66., (1, 180, 1),
        [(0, 0., 1), (2, 1.24702, 1), (4, 3.30822, 1)],
        [(1, 2, be2**.5, 2), (2, 3, rotor_matrix_element(2, 4, q0), 2)])


def _nickel():
    be2, q2 = 0.0650, -0.10
    return tclx_text([
        '58Ni projectile on 208Pb: an almost first-order E2 excitation with a small reorientation term.',
        'E(2+) = 1454.21 keV, Q(2+) = -0.10(6) e b [Nesaraja et al., NDS 111, 897 (2010)]',
        'B(E2; 0+ -> 2+) = 0.0650(12) e2 b2 [Pritychenko et al., ADNDT 107, 1 (2016)]',
        '<0||E2||2> = sqrt(B(E2)); <2||E2||2> from Q(2+) = sqrt(16pi/5) (2 2 2; -2 0 2) <2||E2||2>',
        '220 MeV = 3.79 MeV/u keeps the nuclear surfaces > 5 fm apart at every angle.',
    ], '58Ni + 208Pb, 220 MeV (literature data)', (28, 58), (82, 208), 220., (1, 180, 1),
        [(0, 0., 1), (2, 1.45421, 1)],
        [(1, 2, be2**.5, 2), (2, 2, diagonal_from_quadrupole(2, q2), 2)])


SAMARIUM_BAND = [0., 0.1217818, 0.3664793, 0.706928, 1.12539, 1.60926, 2.14881, 2.73619, 3.36502]


def _samarium():
    q0 = rotor_q0_from_be2(3.4611)
    spins = list(range(0, 17, 2))
    return tclx_text([
        '152Sm beam on a 58Ni target: multi-step excitation of a rotational band, inverse kinematics.',
        'Ground-band energies 0+ ... 16+ [M. J. Martin, NDS 114, 1497 (2013)]',
        'B(E2; 0+ -> 2+) = 3.4611(21) e2 b2 [Pritychenko et al., ADNDT 107, 1 (2016)]',
        f'Rigid-rotor model (Bohr & Mottelson Vol. II): Q0 = sqrt(16pi B/5) = {q0:.4f} e b, and',
        '<I||E2||I\'> = sqrt(2I+1) <I 0 2 0|I\' 0> sqrt(5/16pi) Q0 for every band member (model values).',
        'Check: the rotor predicts Q(2+) = -2/7 Q0 = -1.685 e b; measured -1.683(18) e b [NDS 114].',
        '500 MeV = 3.29 MeV/u keeps the nuclear surfaces > 5 fm apart at every angle.',
        'Check band truncation by adding levels; a small highest-level population alone is not proof.',
    ], '152Sm + 58Ni, 500 MeV (literature data + rigid rotor)', (62, 152), (28, 58), 500., (1, 180, 1),
        [(s, e, 1) for s, e in zip(spins, SAMARIUM_BAND)], _rotor_elements(spins, q0))


def _uranium():
    q0 = rotor_q0_from_be2(12.19)
    spins = [0, 2, 4, 6, 8, 10, 12]
    energies = [0., 0.044916, 0.14838, 0.30718, 0.5181, 0.7759, 1.0767]
    return tclx_text([
        '16O beam on a 238U target (choose "target" as the excited nucleus): multiple excitation.',
        'Ground-band energies 0+ ... 12+ [E. Browne, J. K. Tuli, NDS 127, 191 (2015)]',
        'B(E2; 0+ -> 2+) = 12.19(62) e2 b2 [Pritychenko et al., ADNDT 107, 1 (2016)]',
        f'Rigid-rotor model: Q0 = {q0:.4f} e b for every band member (model values).',
        '66 MeV = 4.13 MeV/u keeps the nuclear surfaces > 5 fm apart at every angle.',
        'Check band truncation by adding levels; a small highest-level population alone is not proof.',
    ], '16O + 238U, 66 MeV, target excitation (literature data + rigid rotor)', (8, 16), (92, 238), 66.,
        (1, 180, 1), [(s, e, 1) for s, e in zip(spins, energies)], _rotor_elements(spins, q0))


def _lead():
    return tclx_text([
        '16O beam on a 208Pb target (choose "target" as the excited nucleus): octupole E3 and E2 excitation.',
        'E(3-) = 2614.522 keV, B(E3; 0+ -> 3-) = 0.611(9) e2 b3, Q(3-) = -0.34(15) e b,',
        'E(2+) = 4085.52 keV, Q(2+) = -0.7(3) e b [M. J. Martin, NDS 108, 1583 (2007)]',
        'B(E2; 0+ -> 2+) = 0.287(18) e2 b2 [Pritychenko et al., ADNDT 107, 1 (2016)]',
        'The very weak 3- <-> 2+ E1 coupling (B(E1) = 0.00035 W.u., NDS 108) is omitted.',
        '60 MeV = 3.75 MeV/u keeps the nuclear surfaces > 5 fm apart at every angle.',
    ], '16O + 208Pb, 60 MeV, target excitation (literature data)', (8, 16), (82, 208), 60., (1, 180, 1),
        [(0, 0., 1), (3, 2.614522, -1), (2, 4.08552, 1)],
        [(1, 2, 0.611**.5, 3), (2, 2, diagonal_from_quadrupole(3, -0.34), 2),
         (1, 3, 0.287**.5, 2), (3, 3, diagonal_from_quadrupole(2, -0.7), 2)])


def _teaching_rotor():
    # 152Sm + 208Pb kinematics; Q0 chosen so that the AW60 parameter is q = 2.
    base = Reaction('rotor', 62, 152, 82, 208, 600., (Level(0., 0.),), ())
    q0 = 2./aw60_q(base, 1.)
    spins = list(range(0, 17, 2))
    return tclx_text([
        'Exactly solvable teaching model: a rigid rotor with all levels at 0 MeV (adiabaticity xi = 0).',
        'At 180 deg the excitation is known in closed form [Alder & Winther, Mat. Fys. Medd. 32, no. 8',
        '(1960), Eq. 5.14]. Their Table 5 gives, for q = 2: P(0)=0.2152, P(2)=0.5597, P(4)=0.1972,',
        'P(6)=0.0260, P(8)=0.0018, P(10)=0.0001. Run 180 deg and compare.',
        'The electric dipole polarization is not part of this model; the app switches it off.',
        f'Kinematics of 152Sm + 208Pb at 600 MeV; Q0 = {q0:.6f} e b gives q = 2.',
    ], 'Teaching model: degenerate rigid rotor, q = 2 (Alder-Winther benchmark)', (62, 152), (82, 208), 600.,
        (120, 180, 20), [(s, 0., 1) for s in spins], _rotor_elements(spins, q0))


EXAMPLES = (
    Example('22Mg + 104Pd', 'literature', '22Mg_104Pd_literature.txt', 'projectile',
            '22Mg radioactive beam (3.0 MeV/u) on 104Pd: 0+, 2+ and 4+ states from evaluated data.',
            'A light nucleus with an uncertain B(E2): the 2+ is excited in one step, the 4+ only weakly in '
            'two steps through a rigid-rotor model element. Q(2+) is not measured and is left out.',
            ('PR16', 'NDS22', 'BM75'),
            data=(Datum('E(2+)', 1.24702, 3e-5, 3e-5, 'MeV', 'NDS22', level_energy(1)),
                  Datum('E(4+)', 3.30822, 6e-5, 6e-5, 'MeV', 'NDS22', level_energy(2)),
                  Datum('B(E2; 0+ → 2+)', 0.034, 0.011, 0.016, 'e² b²', 'PR16', b_up(0, 1, 2))),
            generator=_magnesium),
    Example('58Ni + 208Pb', 'literature', '58Ni_208Pb_literature.txt', 'projectile',
            '58Ni beam (3.79 MeV/u) on 208Pb using evaluated B(E2) and Q(2+).',
            'Weak coupling: the result is close to first-order perturbation theory, with a small reorientation term.',
            ('PR16', 'NDS58'),
            data=(Datum('E(2+)', 1.45421, 9e-5, 9e-5, 'MeV', 'NDS58', level_energy(1)),
                  Datum('B(E2; 0+ → 2+)', 0.0650, 0.0012, 0.0012, 'e² b²', 'PR16', b_up(0, 1, 2)),
                  Datum('Q(2+)', -0.10, 0.06, 0.06, 'e b', 'NDS58', q_spectroscopic(1))),
            generator=_nickel),
    Example('152Sm + 58Ni', 'literature', '152Sm_58Ni_literature.txt', 'projectile',
            '152Sm beam (3.29 MeV/u) on 58Ni: ground band up to 16+, inverse kinematics.',
            'Multi-step excitation of a rotational band. Measured B(E2) fixes Q0; the rigid-rotor model '
            'supplies the other matrix elements and correctly predicts the measured Q(2+). '
            'A heavy beam on a light target gives two lab branches.',
            ('PR16', 'NDS152', 'BM75'),
            data=(Datum('E(2+)', 0.1217818, 3e-7, 3e-7, 'MeV', 'NDS152', level_energy(1)),
                  Datum('E(4+)', 0.3664793, 9e-7, 9e-7, 'MeV', 'NDS152', level_energy(2)),
                  Datum('B(E2; 0+ → 2+)', 3.4611, 0.0021, 0.0021, 'e² b²', 'PR16', b_up(0, 1, 2)),
                  Datum('Q(2+)', -1.683, 0.018, 0.018, 'e b', 'NDS152', q_spectroscopic(1), model=True)),
            generator=_samarium),
    Example('16O + 238U', 'literature', '16O_238U_literature.txt', 'target',
            '16O beam (4.13 MeV/u) on a 238U target; the target is excited (ground band up to 12+).',
            'Multiple Coulomb excitation of a strongly deformed nucleus, even with a light beam. Shows target excitation.',
            ('PR16', 'NDS238', 'BM75'),
            data=(Datum('E(2+)', 0.044916, 1.3e-5, 1.3e-5, 'MeV', 'NDS238', level_energy(1)),
                  Datum('B(E2; 0+ → 2+)', 12.19, 0.62, 0.62, 'e² b²', 'PR16', b_up(0, 1, 2))),
            generator=_uranium),
    Example('16O + 208Pb', 'literature', '16O_208Pb_literature.txt', 'target',
            '16O beam (3.75 MeV/u) on a 208Pb target; the octupole 3− and the 2+ state of 208Pb are excited.',
            'Electric octupole (E3) excitation and the adiabatic suppression of high-lying states.',
            ('NDS208', 'PR16'), angles=(20., 180., 20.),
            data=(Datum('E(3−)', 2.614522, 1e-5, 1e-5, 'MeV', 'NDS208', level_energy(1)),
                  Datum('B(E3; 0+ → 3−)', 0.611, 0.009, 0.009, 'e² b³', 'NDS208', b_up(0, 1, 3)),
                  Datum('Q(3−)', -0.34, 0.15, 0.15, 'e b', 'NDS208', q_spectroscopic(1)),
                  Datum('E(2+)', 4.08552, 4e-5, 4e-5, 'MeV', 'NDS208', level_energy(2)),
                  Datum('B(E2; 0+ → 2+)', 0.287, 0.018, 0.018, 'e² b²', 'PR16', b_up(0, 2, 2)),
                  Datum('Q(2+)', -0.7, 0.3, 0.3, 'e b', 'NDS208', q_spectroscopic(2))),
            generator=_lead),
    Example('Teaching: sudden rotor', 'teaching', 'teaching_sudden_rotor.txt', 'projectile',
            'Exactly solvable model: a rigid rotor with all levels at 0 MeV, q = 2.',
            'At 180° the populations must reproduce the published Alder–Winther (1960) Table 5.',
            ('AW60', 'BM75'), angles=(120., 180., 20.), polarization=False,
            data=(Datum('AW60 parameter q', 2.0, 1e-6, 1e-6, '', 'AW60',
                        lambda r: aw60_q(r, _element(r, 0, 1, 2)/rotor_matrix_element(0, 2, 1.))),),
            generator=_teaching_rotor),
)
BY_KEY = {example.key: example for example in EXAMPLES}

KIND_LABELS = {'literature': 'Literature data', 'teaching': 'Teaching model'}
TABLE_EXAMPLE = '22Mg + 104Pd'   # the filled example offered for the CSV table uploads


def write_example_files(directory=ROOT/'examples'):
    """Export the examples and the filled table examples so they can be used outside the app."""
    for example in EXAMPLES:
        if example.generator:
            (directory/example.filename).write_text(example.text())
    levels, elements = table_texts(BY_KEY[TABLE_EXAMPLE].reaction())
    (directory/'templates/levels.csv').write_text(levels)
    (directory/'templates/matrix_elements.csv').write_text(elements)
