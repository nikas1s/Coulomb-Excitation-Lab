"""Independent spherical-harmonic/unitary checks of isolated E1 and E4.

Run without GOSIA or a compiler: python validation/geometric_benchmark.py
"""
from pathlib import Path
import json
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from validation.gosia_points import cases
from validation.research_qualification.independent_cc import geometric_midpoint
from coulex import CoupledChannels,SolverSettings


def run():
    rows=[]
    # Numerical acceptance before evaluation: independent CODATA constants
    # differ from the rounded legacy constants of the production formalism.
    atol=2e-8;rtol=1e-4
    for reaction in (list(cases())[0],list(cases())[3]):
        for angle in (45.,90.,135.):
            samples=[geometric_midpoint(reaction,angle,steps=n,endpoint=10.) for n in (4000,8000,16000)]
            shorter=geometric_midpoint(reaction,angle,steps=12800,endpoint=8.)
            collision=CoupledChannels(reaction).solve(angle,SolverSettings(rtol=1e-11,atol=1e-14,extra_omega=1.))
            actual=collision.probabilities
            fine=samples[-1]['probabilities'];previous=samples[-2]['probabilities']
            change=abs(fine-previous);tail=abs(fine-shorter['probabilities'])
            match=bool(np.all(abs(actual-fine)<=atol+rtol*abs(fine)))
            density_error=[float(np.max(abs(a-b))) for a,b in zip(collision.density_matrices,samples[-1]['density_matrices'])]
            density_match=all(error<=atol+rtol*probability for error,probability in zip(density_error,fine))
            converged=bool(np.all(change<=1e-7+2e-5*abs(fine)) and np.all(tail<=1e-7+2e-5*abs(fine)))
            norm=max(s['norm_error'] for s in [*samples,shorter])
            row=dict(case=reaction.title,cm_angle=angle,production=actual.tolist(),
                independent=fine.tolist(),step_samples=[s['probabilities'].tolist() for s in samples],
                steps=[4000,8000,16000],endpoint=10.,short_endpoint=8.,
                final_step_change=change.tolist(),endpoint_change=tail.tolist(),
                relative_difference=((actual-fine)/np.maximum(abs(fine),1e-300)).tolist(),
                density_max_error=density_error,density_matched=bool(density_match),
                norm_error=norm,matched=match,converged=converged,passed=bool(match and density_match and converged and norm<1e-9))
            rows.append(row);print(reaction.title,angle,'PASS' if row['passed'] else 'FAIL',flush=True)
    return dict(method='Geometric spherical-harmonic Coulomb Hamiltonian, Wigner–Eckart coupling, CODATA 2018 and unitary midpoint propagation',
                relative_tolerance=rtol,absolute_tolerance=atol,rows=rows,passed=all(r['passed'] for r in rows),
                scope='Isolated E1/E4 target excitation, unpolarized J=0 ground state, finite-energy channels, three CM angles; polarization off')

if __name__=='__main__':
    report=run();path=ROOT/'validation/research_qualification/geometric-reference.json'
    path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    raise SystemExit(0 if report['passed'] else 1)
