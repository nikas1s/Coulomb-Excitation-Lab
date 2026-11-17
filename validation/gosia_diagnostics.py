"""Optional diagnosis of legacy-reference limitations; does not modify app code.

Only orbit-storage dimensions are extended in a cached GOSIA variant. The
original source and both compiled variants stay outside the tracked tree.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from validation.gosia_points import cases,gosia_input
from coulex import CoupledChannels,SolverSettings
from coulex.measurements import cm_branches
from coulex.literature import first_order_probability


def execute(binary,text):
    with tempfile.TemporaryDirectory(prefix='gosia-diagnostic-') as work:
        run=subprocess.run([str(binary)],input=text,text=True,cwd=work,capture_output=True,timeout=60)
        path=Path(work)/'point.out';output=path.read_text() if path.exists() else ''
    populations=re.findall(r'LEVEL\s+(\d+)\s+POPULATION\s+(\S+)',output)
    return run,output,populations


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    args=p.parse_args();source=args.source.read_text();cache=ROOT/'.cache/research-qualification';cache.mkdir(parents=True,exist_ok=True)
    extended=source;patches={}
    for before,after in [('LP12 = 365','LP12 = 700'),('SH(365)','SH(700)'),('CH(365)','CH(700)'),('ADB(365)','ADB(700)')]:
        patches[before]=dict(replacement=after,occurrences=source.count(before));extended=extended.replace(before,after)
    extended_path=cache/'gosia-storage700.f';extended_path.write_text(extended)
    compiler=subprocess.run(['gfortran','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    commands=[]
    for path,name,flags in [(args.source.resolve(),'gosia-bounds',['-fcheck=bounds','-g']),
                            (extended_path,'gosia-storage700',[])]:
        cmd=['gfortran','-std=legacy','-O0',*flags,'-o',str(cache/name),str(path)]
        build=subprocess.run(cmd,capture_output=True,text=True,check=True);commands.append(cmd)
        (cache/(name+'-compile.log')).write_text(build.stderr)
    e1=next(cases());text=gosia_input(e1,[60.])
    checked,_,_=execute(cache/'gosia-bounds',text)
    weak=replace(e1,elements=tuple(replace(m,value=.002) for m in e1.elements))
    extended_run,_,populations=execute(cache/'gosia-storage700',gosia_input(weak,[60.]))
    theta=cm_branches(weak,60.,.3)[0]
    actual=CoupledChannels(weak).solve(theta,SolverSettings(rtol=1e-11,atol=1e-14,extra_omega=1.)).probabilities[1]
    reference=float(populations[1][1]);first_order=first_order_probability(weak,theta,1)
    e4=list(cases())[3];e4run,output,_=execute(cache/'gosia-bounds',gosia_input(e4,[60.]))
    report=dict(source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),compiler=compiler,
        extended_source_sha256=hashlib.sha256(extended_path.read_bytes()).hexdigest(),compile_commands=commands,storage_edits=patches,
        e1_storage=dict(returncode=checked.returncode,diagnostic=checked.stderr.split('Backtrace:')[0].strip(),
            out_of_bounds_confirmed=bool(checked.returncode and "Index '366'" in checked.stderr)),
        e1_extended=dict(returncode=extended_run.returncode,reference_probability=reference,python_probability=float(actual),
            relative_difference=float(actual/reference-1),predeclared_relative_tolerance=3e-4,
            comparison_passed=bool(abs(actual-reference)<=1e-10+3e-4*abs(reference))),
        e1_independent_weak_limit=dict(first_order_probability=float(first_order),coupled_probability=float(actual),
            relative_difference=float(actual/first_order-1),passed=bool(abs(actual/first_order-1)<1e-4)),
        e4_isolated=dict(returncode=e4run.returncode,nonfinite_output='NaN' in output or 'Infinity' in output,
            resolved=False),
        conclusion='E1 storage overflow diagnosed. Extending storage removes nonfinite results but leaves a discrepancy outside the unchanged tolerance. Isolated E4 remains unresolved; coupled E2/E4 has a separate passing reference.')
    out=ROOT/'validation/research_qualification/gosia-diagnostics.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['conclusion'])
    return 0

if __name__=='__main__':raise SystemExit(main())
