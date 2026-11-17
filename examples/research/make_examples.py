"""Regenerate clearly labelled synthetic research fixtures; no experimental data."""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
from sympy.physics.wigner import clebsch_gordan
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from coulex.model import Level,MatrixElement,Reaction
from coulex.literature import rotor_matrix_element
from coulex.workflow import calculate
from coulex.decay import decay_rates

OUT=Path(__file__).resolve().parent

def write_input(name,r):
    lines=[r.title,str(len(r.levels)),f'{r.projectile_z} {r.projectile_a}',f'{r.target_z} {r.target_a}',str(r.energy_lab),'30 180 15']
    lines += [f'{i+1} {l.spin} {l.energy} {l.parity} 0' for i,l in enumerate(r.levels)]
    lines += [f'{m.initial+1} {m.final+1} {m.value:.14g} {m.multipolarity}' for m in r.elements]
    (OUT/name).write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')


def main():
    levels=tuple(Level(j,.02*j*(j+1)) for j in (0,2,4))
    elements=tuple(MatrixElement(i,j,rotor_matrix_element(a.spin,b.spin,2.)) for i,a in enumerate(levels) for j,b in enumerate(levels) if i<=j and abs(a.spin-b.spin)<=2 and a.spin+b.spin>=2)
    r=Reaction('SYNTHETIC rotor research demonstration (not measured)',20,40,82,208,160.,levels,elements,dipole_strength=0.)
    write_input('synthetic_rotor.txt',r)
    angles=[50.,100.,150.]; experiments=[]
    for energy in (140.,160.):
        scan=calculate(r.at_energy(energy),angles)
        data=pd.DataFrame(dict(angle_deg=angles,level=2,value=scan.cross_sections[:,1],uncertainty=scan.cross_sections[:,1]*.03))
        data.to_csv(OUT/f'synthetic_cross_sections_{int(energy)}.csv',index=False)
        experiments.append(dict(kind='cross_section',energy_lab=energy,likelihood='gaussian',normalization_sigma=.03,data=data.to_dict('records')))
    (OUT/'synthetic_joint_fit.json').write_text(json.dumps(dict(parameters=[dict(kind='element',index=1),dict(kind='element',index=2)],bounds=[[.1,-3.],[2.,3.]],starts=[[elements[0].value*.9,elements[1].value*.8],[elements[0].value*1.1,-elements[1].value]],experiments=experiments,max_nfev=80),indent=2)+'\n', encoding='utf-8', newline='\n')
    np.savetxt(OUT/'rotor_covariance.csv',np.diag([(abs(m.value)*.05)**2 for m in elements]),delimiter=',')
    pd.DataFrame([dict(upper=3,lower=2,branch=1.,alpha=0.,multipolarity=2),dict(upper=2,lower=1,branch=1.,alpha=0.,multipolarity=2)]).to_csv(OUT/'rotor_decay.csv',index=False)
    levels=(Level(0,0),Level(2,.12),Level(4,.4),Level(1,.8,-1),Level(3,.92,-1),Level(5,1.2,-1))
    elements=[]
    for i,a in enumerate(levels):
        for j,b in enumerate(levels):
            if i>j: continue
            for lam,q in ((2,2.),(3,.6)):
                if a.parity*b.parity!=(-1)**lam or not abs(a.spin-b.spin)<=lam<=a.spin+b.spin: continue
                cg=float(clebsch_gordan(int(a.spin),lam,int(b.spin),0,0,0))
                value=np.sqrt((2*a.spin+1)*(2*lam+1)/(16*np.pi))*cg*q
                if value: elements.append(MatrixElement(i,j,value,lam))
    octupole=Reaction('SYNTHETIC opposite-parity bands (not measured)',20,40,82,208,160.,levels,tuple(elements),dipole_strength=0.)
    write_input('synthetic_octupole.txt',octupole)

if __name__=='__main__': main()
