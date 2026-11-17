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
from validation.research_qualification.nonlinear import nonlinear_coverage
from validation.research_qualification.checks import published_shapes,angular_algebra,gaussian_coverage,gosia_replay,experimental_inputs
from validation.geometric_benchmark import run as geometric_reference


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
    rows=sum((report['checks'][key]['rows'] for key in ('gosia_points_finite_cases','gosia_expanded','gosia_precision')),[])
    delta=[(r['actual']/r['expected']-1)*1e6 for r in rows]
    axes[1].scatter(np.arange(1,len(rows)+1),delta,color='tab:green')
    axes[1].axhline(0,color='grey',ls='--')
    axes[1].set(xlabel='Finite GOSIA reference point',ylabel='Relative probability difference (ppm)',
                title='Independent point-excitation comparison')
    for ax in axes: ax.grid(alpha=.25)
    fig.savefig(destination/'summary.png',dpi=180)
    fig.savefig(destination/'summary.svg')
    svg=destination/'summary.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()).rstrip()+'\n', encoding='utf-8', newline='\n')
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials',type=int,default=500)
    parser.add_argument('--output',type=Path,default=ROOT/'validation/research_qualification/latest.json')
    parser.add_argument('--extended',action='store_true',help='Also rerun 100 multilevel coupled-channel coverage fits (slow).')
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    checks={}
    for name,function in [('published_shapes',published_shapes),('angular_algebra',angular_algebra),('gosia_points_finite_cases',gosia_replay),
                          ('gosia_expanded',lambda:gosia_replay('gosia_expanded/results.json')),
                          ('gosia_precision',lambda:gosia_replay('gosia_precision/results.json',builds=('unmodified','mesh0.0075'))),
                          ('geometric_reference',geometric_reference),
                          ('gaussian_coverage',lambda:gaussian_coverage(args.trials)),
                          ('nonlinear_coverage',nonlinear_coverage)]:
        print(f'Running {name}…',flush=True)
        checks[name]=function()
        print(f"{name}: {'PASS' if checks[name]['passed'] else 'FAIL'}",flush=True)
    (ROOT/'validation/research_qualification/geometric-reference.json').write_text(json.dumps(checks['geometric_reference'],indent=2,allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    if args.extended:
        from validation.multilevel_coverage import run
        checks['multilevel_coverage']=run()
        (args.output.parent/'multilevel-coverage.json').write_text(json.dumps(checks['multilevel_coverage'],indent=2,allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    files=sorted({str(path.relative_to(ROOT)) for path in (ROOT/'coulex').glob('*.py')} | {
        'validation/qualify.py','validation/geometric_benchmark.py','validation/gosia_precision.py','validation/multilevel_coverage.py',
        'validation/research_qualification/independent_cc.py','validation/research_qualification/geometric-reference.json',
        'validation/research_qualification/gosia_precision/results.json','validation/research_qualification/checks.py','validation/research_qualification/nonlinear.py',
        'validation/research_qualification/lab-response-convergence.json','validation/lab_response_convergence.py',
        'validation/research_qualification/bibliography-search.json',
        'validation/research_qualification/cd106.json','validation/research_qualification/gosia_points/results.json','validation/research_qualification/gosia_expanded/results.json','validation/research_qualification/gosia-diagnostics.json',
        'validation/research_qualification/experiments/sr96_sn120/manifest.json','validation/research_qualification/experiments/sr96_sn120/yields.csv'})
    experimental=experimental_inputs()
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),platform=platform.platform(),
                git_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
                working_tree_dirty=bool(subprocess.run(['git','status','--porcelain'],cwd=ROOT,capture_output=True,text=True).stdout.strip()),
                dependencies={name:importlib.metadata.version(name) for name in ('numpy','scipy','sympy','pandas')},
                hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},checks=checks,
                computational_checks_passed=all(c['passed'] for c in checks.values()),
                research_qualified=False,experimental_target=experimental,
                reference_diagnostics=dict(historical_legacy=json.loads((ROOT/'validation/research_qualification/gosia-diagnostics.json').read_text(encoding='utf-8')),
                    resolution='Specific isolated E1/E4 benchmark issues resolved by independently converged geometric propagation, unmodified newer E4 reference and explicitly mesh-refined E1 reference. Historical failed runs are preserved.'),
                requested_use_cases={
                  'experiment_planning': {'qualified':False,'remaining':'Broader excitation, derivative and integration error budgets'},
                  'nuclear_shape_studies': {'qualified':False,'remaining':'Additional networks, propagated experimental covariance and independent review'},
                  'experimental_gamma_yield_analysis': {'qualified':False,'remaining':'Matched experiment response, normalization, fit reproduction and nonlinear coverage'}},
                remaining_gates=['Broaden excitation, derivative and detector error budgets beyond the independently checked E1–E4 cases',
                'Experimental gamma-yield reproduction with matched geometry, multipoles and all correction inputs',
                'Broader multilevel fit interval coverage, including low counts and fitted detector systematics beyond the recorded Gaussian case',
                'Independent nuclear-physics review and versioned scope sign-off'])
    multilevel=ROOT/'validation/research_qualification/multilevel-coverage.json'
    if multilevel.exists():
        report['archived_multilevel_coverage']=dict(sha256=hashlib.sha256(multilevel.read_bytes()).hexdigest(),
            result=json.loads(multilevel.read_text(encoding='utf-8')),rerun_in_this_command=args.extended)
    convergence=ROOT/'validation/research_qualification/lab-response-convergence.json'
    report['archived_lab_response_convergence']=dict(sha256=hashlib.sha256(convergence.read_bytes()).hexdigest(),
        result=json.loads(convergence.read_text(encoding='utf-8')),rerun_in_this_command=False)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    (args.output.parent/'nonlinear-coverage.json').write_text(json.dumps(checks['nonlinear_coverage'],indent=2,allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    save_figure(report,args.output.parent)
    print('Report:',args.output)
    print('Research qualification remains incomplete: see remaining_gates in the report.')
    return 0 if report['computational_checks_passed'] else 1

if __name__=='__main__': raise SystemExit(main())
