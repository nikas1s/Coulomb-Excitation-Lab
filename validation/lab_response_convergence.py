"""Synthetic finite-bin/depth/mesh convergence of the full fed gamma predictor."""
from pathlib import Path
from dataclasses import asdict
import json
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from coulex import SolverSettings
from coulex.research import Experiment
from coulex.gamma_yields import GammaResponse
from coulex.lab_gamma import GammaMesh
from coulex.decay import Transition
from coulex.measurements import Exposure
from coulex.stopping import StoppingTable
from validation.gosia_points import cases


def run():
    reaction=list(cases())[4]
    data=pd.DataFrame(dict(angle_min_deg=[60.,100.],angle_max_deg=[64.,104.],
                           value=[100.,100.],uncertainty=[5.,5.],efficiency=[.8,.8]))
    edges=(Transition(2,1,1.),Transition(1,0,1.,.1))
    rows=[]
    configurations=[(4,2.,8,8,1e-8),(8,1.,12,16,1e-8),(12,.5,16,32,1e-8),(12,.5,16,32,1e-10)]
    for depth,step,mesh,phi,rtol in configurations:
        detector=GammaMesh.annulus(35.,65.,phi_min_deg=10.,phi_max_deg=80.,efficiency=.4,order=mesh,phi_order=2*mesh,
            energy_mev=[.08,.2,.4],efficiency_curve=[.8,.6,.4])
        experiment=Experiment(data,kind='angular_gamma_counts',transitions=edges,photon_transition=1,
            gamma_response=GammaResponse((detector,),particle_phi_order=phi),
            exposure=Exposure(thickness=.5),stopping=StoppingTable([20.,40.],[1.,1.]),
            particle_acceptance=(15.,60.),detected_particle='either',particle_energy_min_mev=1.,
            order=depth,angular_step=step)
        counts=experiment.predict(reaction,SolverSettings(rtol=rtol,atol=rtol*1e-3))
        rows.append(dict(depth_order=depth,angular_step_deg=step,gamma_polar_order=mesh,
            gamma_phi_order=2*mesh,particle_phi_order=phi,rtol=rtol,counts=counts.tolist()))
        print(rows[-1],flush=True)
    medium,fine,tight=[np.array(row['counts']) for row in rows[1:]]
    quadrature=abs(fine-medium);ode=abs(tight-fine)
    return dict(model=asdict(reaction),configurations=rows,
        quadrature_absolute_tolerance=1e-8,quadrature_relative_tolerance=5e-4,ode_relative_tolerance=1e-5,
        quadrature_change=quadrature.tolist(),ode_change=ode.tolist(),
        passed=bool(np.all(fine>0) and np.all(quadrature<=1e-8+5e-4*abs(fine)) and np.all(ode<=1e-8+1e-5*abs(tight))),
        scope='Synthetic E2 0+/2+/4+ target excitation, two CM particle bins, either-particle lab acceptance, threshold, constant stopping, pure E2 feeding, intrinsic gamma sector and calibration curve; not an experimental detector error budget')


if __name__=='__main__':
    report=run()
    (ROOT/'validation/research_qualification/lab-response-convergence.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    raise SystemExit(0 if report['passed'] else 1)
