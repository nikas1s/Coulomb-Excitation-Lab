"""Optional independent GOSIA point benchmark; compiler/source are not app dependencies.

Compile the official March-2008 GOSIA source in an ignored cache, then run:
python validation/gosia_points.py --binary .cache/research-qualification/gosia --source .cache/research-qualification/gosia.f
Only our generated inputs and numerical results are retained in validation/.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coulex import Reaction,Level,MatrixElement,CoupledChannels,SolverSettings
from coulex.measurements import cm_branches
from coulex.observables import surface_separation


def cases():
    for lam in range(1,5):
        yield Reaction(f'E{lam} isolated',8,16,28,58,30.,(Level(0,0),Level(lam,.3,(-1)**lam)),
                       (MatrixElement(0,1,.2,lam),),excitation='target',dipole_strength=0.)
    yield Reaction('E2 multistep and reorientation',8,16,28,58,30.,(Level(0,0),Level(2,.15),Level(4,.4)),
                   (MatrixElement(0,1,.4),MatrixElement(1,1,-.2),MatrixElement(1,2,.7),MatrixElement(2,2,-.3)),excitation='target',dipole_strength=0.)
    yield Reaction('E2 half-integer unpolarized',8,16,28,58,30.,(Level(.5,0),Level(1.5,.3)),
                   (MatrixElement(0,1,.2),MatrixElement(1,1,-.1)),excitation='target',dipole_strength=0.)


def gosia_input(r,labs):
    lines=['OP,FILE','22,3,1','point.out','0,0,0','OP,TITL','    '+r.title,'OP,COUL','LEVE']
    lines += [f'{i+1},{level.parity},{level.spin},{level.energy}' for i,level in enumerate(r.levels)]
    lines += ['0,0,0,0','ME']
    for lam in sorted({m.multipolarity for m in r.elements}):
        lines.append(f'{lam},0,0,0,0')
        lines += [f'{m.initial+1},{m.final+1},{m.value:.16g},1,1' for m in r.elements if m.multipolarity==lam]
    lines += ['0,0,0,0,0','EXPT',f'{len(labs)},{r.target_z},{r.target_a}']
    lines += [f'{r.projectile_z},{r.projectile_a},{r.energy_lab},{angle},20,0,0,0,360,1,1' for angle in labs]
    lines += ['CONT','DIP,0.','ACC,8.0',f'INT,{len(labs)}.']
    lines += [f'{i+1},1000' for i in range(len(labs))]
    lines += ['PRT,0.','1,-1','0,0','END,','','OP,STAR','OP,EXIT','']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
    args=p.parse_args(); binary=args.binary.resolve()
    source_sha=hashlib.sha256(args.source.read_bytes()).hexdigest()
    out=ROOT/'validation/research_qualification/gosia_points';out.mkdir(parents=True,exist_ok=True)
    labs=[30.,60.,90.];rows=[]
    # Acceptance chosen before running: printed GOSIA populations have seven
    # significant figures; independent constants/algorithms differ slightly.
    relative_tolerance=3e-4; absolute_tolerance=1e-10
    for index,r in enumerate(cases()):
        text=gosia_input(r,labs)
        (out/f'case_{index+1}.inp').write_text(text)
        with tempfile.TemporaryDirectory(prefix='gosia-point-') as work:
            subprocess.run([str(binary)],input=text,text=True,cwd=work,capture_output=True,check=True,timeout=60)
            output=(Path(work)/'point.out').read_text()
        (out/f'case_{index+1}.out').write_text('\n'.join(line.rstrip() for line in output.splitlines()).rstrip()+'\n')
        entries=re.findall(r'LEVEL\s+(\d+)\s+POPULATION\s+([+\-.\dEe]+)',output)
        if len(entries)!=len(labs)*len(r.levels):
            rows.append(dict(case=r.title,passed=False,reference_valid=False,reason='GOSIA incomplete output'))
            continue
        reference=np.array([float(value) for _,value in entries]).reshape(len(labs),len(r.levels))
        solver=CoupledChannels(r)
        for k,lab in enumerate(labs):
            # GOSIA uses the first 2+ state's energy for its default kinematics.
            # Here every case has one excited energy; the multistep case uses .15.
            theta=cm_branches(r,lab,r.levels[1].energy)[0]
            actual=solver.solve(theta,SolverSettings(rtol=1e-11,atol=1e-14,extra_omega=1.)).probabilities
            for level in range(1,len(r.levels)):
                expected=reference[k,level]; difference=abs(actual[level]-expected)
                rows.append(dict(case=r.title,model=asdict(r),lab_angle=lab,cm_angle=theta,level=level+1,
                        surface_separation_fm=float(surface_separation(r,theta)),
                        reference=float(expected),calculated=float(actual[level]),absolute_difference=float(difference),
                        relative_difference=float(difference/max(expected,1e-300)),
                        passed=bool(difference<=absolute_tolerance+relative_tolerance*abs(expected))))
    report=dict(reference='GOSIA March 2008, official Rochester source',source_url='https://www.pas.rochester.edu/~cline/Research/GOSIAcodes/gosia.f',
                source_sha256=source_sha,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                compiler=subprocess.run(['gfortran','--version'],text=True,capture_output=True).stdout.splitlines()[0],
                compile_command='gfortran -std=legacy -O0 -o gosia gosia.f',
                relative_tolerance=relative_tolerance,absolute_tolerance=absolute_tolerance,rows=rows,
                scope='Unpolarized target excitation, electric E1-E4, isolated/multistep/half-integer point populations, polarization off; no gamma response',
                passed=all(row['passed'] for row in rows))
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    for row in rows: print(row['case'],row.get('lab_angle'),row.get('level'),row.get('relative_difference'),row['passed'])
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
