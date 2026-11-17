"""Offline research qualification: python run.py --qualify [--trials 500]."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import os
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from validation.research_qualification.checks import published_shapes,angular_algebra,gaussian_coverage,gosia_replay,experimental_inputs


def save_figure(report, destination):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    coverage=report['checks']['gaussian_coverage']
    values=coverage['intervals']
    for name,entry in values.items():
        x=float(name); y=entry['observed']; lo,hi=entry['binomial_99_interval']
        axes[0].errorbar(x,y,yerr=[[y-lo],[hi-y]],fmt='o',capsize=5,color='tab:blue')
    axes[0].plot([.58,1],[.58,1],ls='--',color='grey')
    axes[0].set(xlabel='Nominal interval coverage',ylabel='Empirical coverage (99% binomial interval)',
                title=f'Gaussian Q constraint: {coverage["trials"]} trials',xlim=(.58,1),ylim=(.58,1))
    rows=report['checks']['gosia_points_finite_cases']['rows']
    delta=[(r['actual']/r['expected']-1)*1e6 for r in rows]
    axes[1].scatter(np.arange(1,len(rows)+1),delta,color='tab:green')
    axes[1].axhline(0,color='grey',ls='--')
    axes[1].set(xlabel='Finite GOSIA reference point',ylabel='Relative probability difference (ppm)',
                title='Independent point-excitation comparison')
    for ax in axes: ax.grid(alpha=.25)
    fig.savefig(destination/'summary.png',dpi=180)
    fig.savefig(destination/'summary.svg')
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials',type=int,default=500)
    parser.add_argument('--output',type=Path,default=ROOT/'validation/research_qualification/latest.json')
    args=parser.parse_args()
    checks={}
    for name,function in [('published_shapes',published_shapes),('angular_algebra',angular_algebra),('gosia_points_finite_cases',gosia_replay),
                          ('gaussian_coverage',lambda:gaussian_coverage(args.trials))]:
        print(f'Running {name}…',flush=True)
        checks[name]=function()
        print(f"{name}: {'PASS' if checks[name]['passed'] else 'FAIL'}",flush=True)
    files=sorted({str(path.relative_to(ROOT)) for path in (ROOT/'coulex').glob('*.py')} | {
        'validation/qualify.py','validation/research_qualification/checks.py',
        'validation/research_qualification/cd106.json','validation/research_qualification/gosia_points/results.json',
        'validation/research_qualification/experiments/sr96_sn120/manifest.json','validation/research_qualification/experiments/sr96_sn120/yields.csv'})
    experimental=experimental_inputs()
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),platform=platform.platform(),
                git_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
                working_tree_dirty=bool(subprocess.run(['git','status','--porcelain'],cwd=ROOT,capture_output=True,text=True).stdout.strip()),
                dependencies={name:importlib.metadata.version(name) for name in ('numpy','scipy','sympy','pandas')},
                hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},checks=checks,
                computational_checks_passed=all(c['passed'] for c in checks.values()),
                research_qualified=False,experimental_target=experimental,
                requested_use_cases={
                  'experiment_planning': {'qualified':False,'remaining':'Broader excitation, derivative and integration error budgets'},
                  'nuclear_shape_studies': {'qualified':False,'remaining':'Additional networks, propagated experimental covariance and independent review'},
                  'experimental_gamma_yield_analysis': {'qualified':False,'remaining':'Matched experiment response, normalization, fit reproduction and nonlinear coverage'}},
                remaining_gates=['Broader independent point-excitation coverage: projectile excitation, polarization and usable E1/E4 references',
                'Experimental gamma-yield reproduction with matched geometry, multipoles and all correction inputs',
                'Nonlinear coupled-channel fit interval coverage, including low counts and normalization systematics',
                'Independent nuclear-physics review and versioned scope sign-off'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    save_figure(report,args.output.parent)
    print('Report:',args.output)
    print('Research qualification remains incomplete: see remaining_gates in the report.')
    return 0 if report['computational_checks_passed'] else 1

if __name__=='__main__': raise SystemExit(main())
