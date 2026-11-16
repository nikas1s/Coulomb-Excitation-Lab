"""Single source of truth for every file the app accepts.

The UI renders these specifications next to each uploader and in the
"File formats" tab; text is English and translated by :mod:`coulex.i18n`.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    name: str
    required: bool
    unit: str
    meaning: str


@dataclass(frozen=True)
class FileFormat:
    key: str
    title: str
    purpose: str
    where: str
    extensions: tuple[str, ...]
    columns: tuple[Column, ...]
    notes: tuple[str, ...]
    example: str            # path of a filled example file, relative to the app folder
    example_label: str

    def blank_template(self):
        """Header-only CSV: every column, no example numbers."""
        return ','.join(column.name for column in self.columns)+'\n'


CSV_RULES = (
    'Save spreadsheets as “CSV UTF-8”. Excel .xlsx workbooks are not read directly.',
    'The first row holds the column names exactly as listed (lower case, no units, no spaces).',
    'Separators: comma, semicolon or tab. Decimal commas are accepted only with semicolon or tab separators.',
    'Numbers only in numeric cells: no units, no thousands separators, no formulas, no percent signs.',
    'Optional columns may be omitted or left blank. Extra columns are ignored.',
)

TCLX_LINES = (
    ('1', 'Title', 'Free text on one line', '22Mg + 104Pd'),
    ('2', 'N', 'Number of nuclear levels (integer)', '3'),
    ('3', 'Z A', 'Projectile charge and mass number (integers)', '12 22'),
    ('4', 'Z A', 'Target charge and mass number (integers)', '46 104'),
    ('5', 'E', 'Beam energy in total MeV (not MeV/u)', '67'),
    ('6', 'θmin θmax Δθ', 'CM angle range in degrees; θmax = 0 means a single angle', '1 180 1'),
    ('7 … 6+N', 'index J E π K', 'One row per level: index 1…N, spin, energy (MeV), parity +1/−1, K (metadata, use 0). '
                                  'Level 1 is the ground state at 0 MeV.', '2 2 1.247 1 0'),
    ('rest', 'i f M λ', 'One row per electric matrix element: level numbers i and f, signed reduced matrix element '
                         '<i‖Eλ‖f> in e·b^(λ/2), multipolarity λ = 1…4. Use i = f for a diagonal '
                         '(reorientation) element. Do not add the reversed pair.', '1 2 0.4687 2'),
)
TCLX_NOTES = (
    'Values on a line are separated by spaces or tabs.',
    'Text after # or // is a comment and is ignored.',
    'The excited nucleus (projectile or target) is chosen in the sidebar, not in the file.',
)
TCLX_TEMPLATE = '''# Reaction text input. Lines beginning with # are comments and are ignored.
# Replace every <...> placeholder with your numbers, then upload the file.
# 1) Title (one line of free text)
<title of your reaction>
# 2) Number of levels N
<N>
# 3) Projectile: Z A
<Z_projectile> <A_projectile>
# 4) Target: Z A
<Z_target> <A_target>
# 5) Beam energy in TOTAL MeV (not MeV/u)
<beam energy>
# 6) CM angles: minimum maximum step (degrees)
<theta_min> <theta_max> <theta_step>
# 7) N level rows: index spin energy_MeV parity(+1/-1) K(0). Level 1: ground state at 0 MeV.
1 <spin> 0 <parity> 0
2 <spin> <energy> <parity> 0
# 8) Matrix-element rows: initial final value[e b^(lambda/2)] lambda(1-4)
1 2 <value> <lambda>
'''

FORMATS = {
    'tclx': FileFormat(
        'tclx', 'Reaction text input', 'Defines the nuclei, beam energy, levels and matrix elements in one text file.',
        'Sidebar → 1 · Reaction → Upload a reaction file', ('.txt', '.dat'), (), TCLX_NOTES,
        'examples/22Mg_104Pd_literature.txt', 'Example file (22Mg + 104Pd)'),
    'levels': FileFormat(
        'levels', 'Nuclear levels table', 'One row per nuclear level of the excited nucleus.',
        'Sidebar → 1 · Reaction → Enter tables, then the level table on the main page', ('.csv', '.tsv', '.txt'),
        (Column('level', True, '—', 'Level number 1, 2, 3 … in order, without gaps'),
         Column('spin', True, 'ħ', 'Spin J: integer or half-integer (0, 2, 1.5 …)'),
         Column('energy_mev', True, 'MeV', 'Excitation energy; level 1 must be the ground state at 0'),
         Column('parity', True, '—', 'Parity: 1 for +, −1 for −'),
         Column('k', False, '—', 'K quantum number, kept as metadata only (default 0)')),
        ('All spins must be either integer or half-integer.',
         'Every level must lie below the centre-of-mass energy.'),
        'examples/templates/levels.csv', 'Example file (22Mg levels)'),
    'matrix_elements': FileFormat(
        'matrix_elements', 'Electric matrix-elements table', 'One row per electromagnetic coupling between two levels.',
        'Sidebar → 1 · Reaction → Enter tables, then the matrix-element table on the main page',
        ('.csv', '.tsv', '.txt'),
        (Column('initial', True, '—', 'Level number of the first state'),
         Column('final', True, '—', 'Level number of the second state (equal to initial for a diagonal element)'),
         Column('value', True, 'e·b^(λ/2)', 'Signed reduced matrix element <initial‖Eλ‖final> (e·b for E2). '
                                            'Not B(Eλ): for a 0+ ground state, value = ±√B(Eλ↑)'),
         Column('lambda', True, '—', 'Electric multipolarity λ = 1, 2, 3 or 4')),
        ('Enter each pair once; the reversed element is generated with the correct phase.',
         'Spin triangle and parity selection rules are checked.',
         'A table with headers only describes a nucleus without couplings.'),
        'examples/templates/matrix_elements.csv', 'Example file (22Mg couplings)'),
    'stopping': FileFormat(
        'stopping', 'Stopping-power table', 'Energy loss of the beam in the target, for thick-target averages.',
        'Sidebar → 3 · Target and energy loss', ('.csv',),
        (Column('energy_mev', True, 'MeV', 'Beam energy (total MeV), strictly increasing'),
         Column('stopping_mev_per_mg_cm2', True, 'MeV/(mg/cm²)', 'Stopping power of this ion in this target material')),
        ('Comma-separated, with exactly these two column names.',
         'At least two rows. The table must cover the incident energy and the exit energy; nothing is extrapolated.',
         'Use a validated table (for example from SRIM or ATIMA) for your ion and material.'),
        'examples/synthetic_stopping.csv', 'Synthetic test table (not physical data)'),
    'cross_section': FileFormat(
        'cross_section', 'Measured differential cross sections', 'Point measurements dσ/dΩ versus angle.',
        'Measurements tab → Differential cross sections', ('.csv', '.tsv', '.txt'),
        (Column('angle_deg', True, '°', 'Scattering angle (CM or lab, as selected); lab angles refer to the scattered projectile'),
         Column('level', True, '—', 'Final level number'),
         Column('value', True, 'barn/sr, mb/sr or fm²/sr', 'Measured dσ/dΩ in the unit selected in the app'),
         Column('uncertainty', False, 'same as value', 'One-sigma standard uncertainty; blank = unknown')),
        (), 'examples/templates/cross_section.csv', 'Example file (synthetic numbers)'),
    'probability': FileFormat(
        'probability', 'Measured population probabilities', 'Point measurements of level populations versus CM angle.',
        'Measurements tab → Population probabilities', ('.csv', '.tsv', '.txt'),
        (Column('angle_deg', True, '°', 'CM scattering angle'),
         Column('level', True, '—', 'Final level number'),
         Column('value', True, '—', 'Probability between 0 and 1'),
         Column('uncertainty', False, '—', 'One-sigma standard uncertainty; blank = unknown')),
        (), 'examples/templates/probability.csv', 'Example file (synthetic numbers)'),
    'particle_counts': FileFormat(
        'particle_counts', 'Detected particle counts', 'Counts of scattered particles per detector angular bin.',
        'Measurements tab → Detected particle counts', ('.csv', '.tsv', '.txt'),
        (Column('angle_min_deg', True, '°', 'Lower edge of the angular bin'),
         Column('angle_max_deg', True, '°', 'Upper edge of the angular bin'),
         Column('level', True, '—', 'Final level number'),
         Column('value', True, 'counts', 'Observed number of counts in the bin'),
         Column('uncertainty', False, 'counts', 'One-sigma standard uncertainty; blank = unknown'),
         Column('efficiency', True, '0–1', 'Particle detection efficiency as a fraction (0.9, not 90)')),
        ('Beam rate, live time and azimuth coverage are entered in the app.',),
        'examples/templates/particle_counts.csv', 'Example file (synthetic numbers)'),
    'gamma_counts': FileFormat(
        'gamma_counts', 'Particle–gamma coincidence counts', 'Coincidences of a direct gamma ray with the scattered particle.',
        'Measurements tab → Direct gamma coincidence counts', ('.csv', '.tsv', '.txt'),
        (Column('angle_min_deg', True, '°', 'Lower edge of the angular bin'),
         Column('angle_max_deg', True, '°', 'Upper edge of the angular bin'),
         Column('level', True, '—', 'Emitting (excited) level number, not 1'),
         Column('value', True, 'counts', 'Observed coincidences in the bin'),
         Column('uncertainty', False, 'counts', 'One-sigma standard uncertainty; blank = unknown'),
         Column('efficiency', True, '0–1', 'Particle detection efficiency'),
         Column('branching_fraction', True, '0–1', 'Direct gamma branch per population'),
         Column('gamma_efficiency', True, '0–1', 'Absolute gamma detection efficiency')),
        ('Feeding cascades, internal conversion and angular correlations are not modelled.',),
        'examples/templates/gamma_counts.csv', 'Example file (synthetic numbers)'),
}
MEASUREMENT_FORMATS = ('cross_section', 'probability', 'particle_counts', 'gamma_counts')
