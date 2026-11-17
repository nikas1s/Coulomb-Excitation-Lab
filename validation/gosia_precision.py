"""Reproduce isolated E1/E4 reference diagnostics with explicit mesh refinement.

Obtain gosia_20110524.13.f from the maintainer page, store only in .cache, run:
python validation/gosia_precision.py --source .cache/research-qualification/gosia-current.f
The reference source is never redistributed. Storage and orbit mesh are the
only edits. Unmodified E4 results are recorded separately from refined E1/E4.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from validation.gosia_points import cases,gosia_input
from validation.gosia_diagnostics import execute
from coulex import CoupledChannels,SolverSettings
from coulex.measurements import cm_branches


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args();original=args.source.read_text()
    if 'DATA fct/0./' not in original or 'LP12 = 365' not in original:
        raise ValueError('Use the specified maintainer version; unexpected source layout.')
    cache=ROOT/'.cache/research-qualification';cache.mkdir(parents=True,exist_ok=True)
    out=ROOT/'validation/research_qualification/gosia_precision';out.mkdir(parents=True,exist_ok=True)
    compiler=subprocess.run(['gfortran','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    builds=[];rows=[];diagnostics=[]
    for mesh in (None,.015,.0075):
        source=original;edits=[];name='unmodified' if mesh is None else f'mesh{mesh}'
        if mesh is not None:
            for before,after in [('LP12 = 365','LP12 = 3000'),('SH(365)','SH(3000)'),('CH(365)','CH(3000)'),('ADB(365)','ADB(3000)'),
                                 ('icnt.EQ.365','icnt.EQ.3000'),('only do 365 steps','only do 3000 steps')]:
                count=source.count(before)
                if not count: raise ValueError('Missing expected reference storage declaration: '+before)
                source=source.replace(before,after);edits.append(dict(before=before,after=after,count=count))
            source,count=re.subn(r'\.03(?![0-9])',f'{mesh:.4f}',source)
            edits.append(dict(before=r'\.03(?![0-9])',after=f'{mesh:.4f}',count=count))
        path=cache/f'gosia-precision-{name}.f';path.write_text(source)
        binary=cache/f'gosia-precision-{name}'
        command=['gfortran','-std=legacy','-ffixed-line-length-none','-O0','-o',str(binary),str(path)]
        build=subprocess.run(command,capture_output=True,text=True,check=True)
        (cache/f'gosia-precision-{name}-build.log').write_text(build.stderr)
        builds.append(dict(name=name,mesh=.03 if mesh is None else mesh,edits=edits,
            source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),compile_command=command))
        for reaction in (list(cases())[0],list(cases())[3]):
            for lab in (30.,60.,90.):
                text=gosia_input(reaction,[lab]);run,output,populations=execute(binary,text)
                stem=f'{name}-E{reaction.levels[1].spin:g}-{lab:g}'
                (out/(stem+'.inp')).write_text(text)
                (out/(stem+'.out')).write_text('\n'.join(line.rstrip() for line in output.splitlines()).rstrip()+'\n')
                if len(populations)!=len(reaction.levels):
                    diagnostics.append(dict(build=name,case=reaction.title,lab_angle=lab,returncode=run.returncode,
                        diagnostic=(run.stdout+run.stderr).strip(),reference_valid=False))
                    continue
                reference=float(populations[1][1])
                theta=cm_branches(reaction,lab,reaction.levels[1].energy)[0]
                actual=CoupledChannels(reaction).solve(theta,SolverSettings(rtol=1e-11,atol=1e-14,extra_omega=1.)).probabilities[1]
                rows.append(dict(build=name,case=reaction.title,model=asdict(reaction),lab_angle=lab,cm_angle=theta,level=2,
                    reference=reference,calculated=float(actual),relative_difference=float(actual/reference-1),
                    passed=bool(abs(actual-reference)<=1e-10+3e-4*abs(reference))))
                print(name,reaction.title,lab,rows[-1]['relative_difference'],rows[-1]['passed'],flush=True)
    fine=[r for r in rows if r['build']=='mesh0.0075']
    untouched_e4=[r for r in rows if r['build']=='unmodified' and r['case']=='E4 isolated']
    report=dict(source_url='https://apps.ikp.uni-koeln.de/~warr/gosia/gosia_20110524.13.f',
        reference='GOSIA maintainer version 24 February 2026; explicitly separated unmodified and storage/mesh-refined runs',
        source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),compiler=compiler,builds=builds,rows=rows,diagnostics=diagnostics,
        absolute_tolerance=1e-10,relative_tolerance=3e-4,
        scope='Isolated E1/E4 target-excitation point populations, three lab angles; polarization off; fine mesh is a modified numerical reference',
        passed=bool(len(fine)==6 and len(untouched_e4)==3 and all(r['passed'] for r in fine+untouched_e4)))
    (out/'results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
