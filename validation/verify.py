"""Check the Python solver against archived numerical reference data; no C++ is required."""
import argparse
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'matplotlib'))
import numpy as np
import pandas as pd
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from coulex import CoupledChannels, SolverSettings, parse_input
from coulex.observables import cross_sections


INPUTS = ROOT/'validation/tclx_inputs'
UPSTREAM = 'https://github.com/jhenderson88/TCLX'


class MissingComparisonInputs(FileNotFoundError):
    """The TCLX example inputs are not distributed with this project (TCLX has no licence)."""


def load_inputs(manifest, inputs=INPUTS):
    """Parse the comparison inputs after checking that they are the files used for the archive."""
    inputs = Path(inputs)
    missing = [name for name in manifest['examples_sha256'] if not (inputs/name).exists()]
    if missing:
        raise MissingComparisonInputs(
            f'Missing comparison inputs in {inputs}: {", ".join(missing)}. TCLX has no licence, so these files are '
            f'not distributed with this project. Download them from {UPSTREAM} as described in '
            'validation/tclx_inputs/README.md.')
    models = {}
    for filename, expected in manifest['examples_sha256'].items():
        path = inputs/filename
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Comparison input changed: {filename}')
        models[path.stem] = parse_input(path.read_text(encoding='utf-8'))
    return models


def load_reference(root=ROOT):
    """Validate the archived evidence (hashes, completeness, finite values) before comparing numbers."""
    archive = root/'validation/results'
    checksums = json.loads((archive/'checksums.json').read_text(encoding='utf-8'))
    for filename, expected in checksums.items():
        if hashlib.sha256((archive/filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Archived reference file changed: {filename}')
    manifest = json.loads((archive/'manifest.json').read_text(encoding='utf-8'))
    frame = pd.read_csv(archive/'comparison.csv')
    # Every level of every case at every angle, exactly once; level counts are checked against the
    # inputs themselves when those are available (load_inputs and tests/test_reference.py).
    levels = frame.groupby('example')['level'].max()
    expected_rows = {(Path(name).stem, angle, level) for name in manifest['examples_sha256']
                     for angle in manifest['angles'] for level in range(1, int(levels.get(Path(name).stem, 0))+1)}
    actual_rows = list(frame[['example', 'theta_cm_deg', 'level']].itertuples(index=False, name=None))
    if len(actual_rows) != len(expected_rows) or set(actual_rows) != expected_rows:
        raise ValueError('Archived comparison is incomplete or contains duplicate rows.')
    if not np.isfinite(frame[['original_probability', 'original_cs_barn_sr']].to_numpy()).all():
        raise ValueError('Archived comparison contains nonfinite values.')
    return frame, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='Compare both examples at every integer angle, 1–180°.')
    parser.add_argument('--inputs', type=Path, default=INPUTS,
                        help='Folder with the two TCLX example inputs (default: validation/tclx_inputs).')
    args = parser.parse_args()
    angles = list(range(1, 181)) if args.full else [1, 5, 15, 30, 60, 90, 120, 150, 175, 180]
    reference_data, reference_manifest = load_reference()
    try:
        models = load_inputs(reference_manifest, args.inputs)
    except MissingComparisonInputs as error:
        print(error, file=sys.stderr)
        return 2
    output = ROOT / 'validation' / 'current'
    output.mkdir(exist_ok=True)
    settings = SolverSettings()
    rows, convergence = [], []
    start = time.perf_counter()
    for filename in sorted(reference_manifest['examples_sha256']):
        example = args.inputs/filename
        model = replace(models[example.stem], polarization_convention='reference')
        n = len(model.levels)
        reference = reference_data[reference_data.example == example.stem].set_index(['theta_cm_deg', 'level'])
        solver = CoupledChannels(model)
        for index, angle in enumerate(angles):
            result = solver.solve(angle, settings)
            cs = cross_sections(model, [angle], result.probabilities[None,:])[0]
            for level in range(n):
                rows.append(dict(example=example.stem, theta_cm_deg=angle, level=level+1,
                                 original_probability=reference.loc[(angle, level+1), 'original_probability'], python_probability=result.probabilities[level],
                                 original_cs_barn_sr=reference.loc[(angle, level+1), 'original_cs_barn_sr'], python_cs_barn_sr=cs[level],
                                 norm_error=result.norm_error))
            if index % 10 == 0:
                print(f'{example.stem}: {index+1}/{len(angles)} angles', flush=True)
        # Different solver, tighter error control, and independent tail extension.
        for angle in (30,90,150):
            base = solver.solve(angle, settings)
            tight = solver.solve(angle, replace(settings, rtol=1e-11, atol=1e-14, max_step=.04))
            tail = solver.solve(angle, replace(settings, extra_omega=1.0))
            rk45 = solver.solve(angle, replace(settings, method='RK45', rtol=1e-10, atol=1e-13))
            convergence.append(dict(example=example.stem, theta_cm_deg=angle,
                                    tighter_ode_max_abs=float(max(abs(base.probabilities-tight.probabilities))),
                                    extended_tail_max_abs=float(max(abs(base.probabilities-tail.probabilities))),
                                    rk45_max_abs=float(max(abs(base.probabilities-rk45.probabilities))),
                                    max_norm_error=base.norm_error))
    data = pd.DataFrame(rows)
    data['absolute_probability_error'] = abs(data.python_probability-data.original_probability)
    data['absolute_cs_error_barn_sr'] = abs(data.python_cs_barn_sr-data.original_cs_barn_sr)
    data.to_csv(output/'comparison.csv', index=False)
    pd.DataFrame(convergence).to_csv(output/'convergence.csv', index=False)
    manifest = dict(python=sys.version, platform=platform.platform(), numpy=np.__version__, scipy=scipy.__version__,
                    reference='archived numerical outputs in validation/results', settings=asdict(settings), angles=angles,
                    polarization_convention='reference',
                    elapsed_seconds=time.perf_counter()-start,
                    reference_files_sha256=json.loads((ROOT/'validation/results/checksums.json').read_text(encoding='utf-8')),
                    examples_sha256={name: hashlib.sha256((args.inputs/name).read_bytes()).hexdigest()
                                     for name in sorted(reference_manifest['examples_sha256'])})
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
    maximum = data.absolute_probability_error.max()
    passing = np.allclose(data.python_probability, data.original_probability, atol=1e-6, rtol=2e-5)
    convergence_pass = all(max(c['tighter_ode_max_abs'],c['extended_tail_max_abs'],c['rk45_max_abs']) < 1e-7 for c in convergence)
    fig, axes = plt.subplots(2,2, figsize=(11,7), constrained_layout=True)
    for col, (example, group) in enumerate(data.groupby('example')):
        for level, state in group.groupby('level'):
            if level > 5:
                continue
            axes[0,col].plot(state.theta_cm_deg,state.python_probability,label=f'Level {level}')
            stride=max(1,len(state)//15)
            axes[0,col].plot(state.theta_cm_deg.iloc[::stride],state.original_probability.iloc[::stride],
                             linestyle='none',marker='o',markersize=3,fillstyle='none',color=axes[0,col].lines[-1].get_color())
        axes[0,col].set(title=example.replace('_example',''),ylabel='Population probability')
        axes[0,col].legend(fontsize=8)
        error = group.groupby('theta_cm_deg').absolute_probability_error.max()
        axes[1,col].semilogy(error.index, np.maximum(error.values,1e-18))
        axes[1,col].set(xlabel='CM scattering angle (degrees)',ylabel='Maximum |Python − original|')
        axes[1,col].grid(alpha=.2)
    fig.suptitle('Python curves and original C++ markers; no renormalization')
    fig.savefig(output/'original_comparison.png', dpi=170)
    plt.close(fig)
    report = [f'# Python regression against archived reference results\n',
              'Comparison with archived [TCLX](https://github.com/jhenderson88/TCLX) output; only Python was executed in this run, using '
              '`polarization_convention="reference"` to match its model settings. '
              'The app uses the literature mass convention (`standard`); its polarized results differ.\n',
              f'Executed {len(angles)} angles for each supplied example ({len(data)} level/angle comparisons).\n',
              f'Archived-reference agreement: **{"PASS" if passing else "FAIL"}**. Convergence: **{"PASS" if convergence_pass else "FAIL"}**.\n',
              f'Maximum absolute population difference: **{maximum:.6g}**.\n',
              'Acceptance against the historical integrator: `abs(P_python − P_cpp) ≤ 1e-6 + 2e-5*abs(P_cpp)`. '
              'This is a regression threshold, not an estimate of physical uncertainty.\n',
              '| Example | Max probability difference | Max norm drift | Max cross-section difference (b/sr) |',
              '|---|---:|---:|---:|']
    for example, group in data.groupby('example'):
        report.append(f'| {example} | {group.absolute_probability_error.max():.6g} | {group.norm_error.max():.6g} | {group.absolute_cs_error_barn_sr.max():.6g} |')
    report += ['\n## Independent numerical checks\n',
               '| Example / angle | Tighter ODE | Longer orbit | RK45 vs DOP853 |', '|---|---:|---:|---:|']
    for c in convergence:
        report.append(f"| {c['example']} / {c['theta_cm_deg']}° | {c['tighter_ode_max_abs']:.4g} | {c['extended_tail_max_abs']:.4g} | {c['rk45_max_abs']:.4g} |")
    report += ['\nEach entry is a maximum absolute population change across all levels. Target: <1e-7. '
               'This does not certify relative accuracy for extremely small populations.\n',
               '![Original comparison](original_comparison.png)\n',
               '## What was executed\n',
               'This run evaluated only the Python solver. The archived reference was produced before source removal '
               'with a tested minimal ROOT adapter, rather than a full ROOT/GSL installation. '
               'It covers E2 projectile excitation from J=0. Other multipoles have independent literature checks.\n',
               'The CSV files contain every comparison, including tiny populations and unnormalized norm diagnostics. '
               'The JSON manifest records input hashes, archived-evidence hashes, dependency versions and solver settings.\n']
    (output/'REPORT.md').write_text('\n'.join(report), encoding='utf-8', newline='\n')
    print(f'Max |ΔP| = {maximum:.6g}; archived-reference agreement={passing}; convergence={convergence_pass}',flush=True)
    return 0 if passing and convergence_pass else 1

if __name__=='__main__':
    raise SystemExit(main())
