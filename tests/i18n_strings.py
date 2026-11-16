"""Collect every interface string that must have a Greek translation (used by tests)."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_FILES = ['app.py', *[f'coulex/{n}.py' for n in ('help_ui', 'input_ui', 'measurement_ui', 'verification_ui', 'plots')]]


def literal_t_calls():
    found = set()
    for name in UI_FILES:
        tree = ast.parse((ROOT/name).read_text())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 't'
                    and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                found.add(node.args[0].value)
    return found


def dynamic_strings():
    """Texts passed to t() through variables: formats, examples, benchmark labels, tab names."""
    from coulex.formats import CSV_RULES, FORMATS, TCLX_LINES
    from coulex.examples import EXAMPLES, KIND_LABELS
    from coulex.measurement_ui import KIND_LABELS as MEASUREMENT_LABELS
    found = set(CSV_RULES) | set(KIND_LABELS.values()) | set(MEASUREMENT_LABELS.values())
    for fmt in FORMATS.values():
        found |= {fmt.title, fmt.purpose, fmt.where, fmt.example_label, *fmt.notes, *(c.meaning for c in fmt.columns)}
    found |= {meaning for _, _, meaning, _ in TCLX_LINES} | {'rest', 'Title'}
    for example in EXAMPLES:
        found |= {example.summary, example.focus}
    found |= {'AW60 parameter q', 'same as value', 'counts', '—'}
    found |= {'Rutherford scattering', 'First-order perturbation theory', 'Sudden limit, two states',
              'Sudden limit, rigid rotor', 'Elastic dσ/dΩ at θcm = 90° (barn/sr)', 'E{lam} 0+ → {state}, P at θcm = {theta}°',
              'P(2+) = sin²χ for χ = 1, θcm = 180°, ξ = 0',
              'Formula reproduces AW60 Table 4 amplitudes (max |ΔRe|, |ΔIm|)',
              'q = {q}: P_I (I = 0…{top}), largest deviation at I = {worst}',
              'Tighter ODE tolerance', 'Orbit extended by Δω=1', 'Independent RK45 integrator',
              'Level scheme', 'Results', 'During the collision', 'Detector yields', 'Measurements',
              'Guide', 'Verification', 'File formats', 'Physics', 'Projectile', 'Target', 'probability', 'counts'}
    return found
