"""Generate self-contained teaching inputs for the new detector/target workflows.

Select synthetic_rotor.txt in the sidebar before uploading these fit files.
Both structures and all observations are synthetic, not measured nuclear data.
"""
from dataclasses import asdict,replace
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from coulex.research import Experiment
from coulex.lab_gamma import GammaMesh
from coulex.gamma_yields import GammaResponse
from coulex.decay import Transition
from coulex.measurements import Exposure


def main():
    out=Path(__file__).resolve().parent
    # Same physical model as the existing sidebar teaching fixture.
    from coulex import Reaction,Level,MatrixElement
    from coulex.literature import rotor_matrix_element
    levels=tuple(Level(j,.02*j*(j+1)) for j in (0,2,4))
    elements=tuple(MatrixElement(i,j,rotor_matrix_element(a.spin,b.spin,2.)) for i,a in enumerate(levels) for j,b in enumerate(levels)
                   if i<=j and abs(a.spin-b.spin)<=2 and a.spin+b.spin>=2)
    primary=Reaction('SYNTHETIC rotor research demonstration (not measured)',20,40,82,208,160.,levels,elements,dipole_strength=0.)
    target=replace(primary,title='SYNTHETIC target, not measured',excitation='target',
        levels=(Level(0,0),Level(2,.3)),elements=(MatrixElement(0,1,.3),))
    definition=asdict(target)
    for element in definition['elements']: element['initial']+=1;element['final']+=1
    experiments=[]
    for name,reaction in [('primary',primary),('target',target)]:
        frame=pd.DataFrame(dict(angle_deg=[60.,110.],level=[2,2],value=[0.,0.],uncertainty=[1.,1.]))
        frame['value']=1.2*Experiment(frame).predict(reaction);frame['uncertainty']=.03*frame.value
        experiments.append(dict(kind='cross_section',model=name,normalization_group='same_beam',data=frame.to_dict('records')))
    (out/'synthetic_target_normalization.json').write_text(json.dumps(dict(
        description='SYNTHETIC: upload synthetic_rotor.txt first and switch polarization OFF. Fixed known target structure normalizes projectile data; planted scale=1.2.',
        models={'target':definition},parameters=[dict(kind='element',index=1)],
        bounds=[[.1],[2.]],starts=[[elements[0].value*.9],[elements[0].value*1.1]],experiments=experiments,max_nfev=50),indent=2)+'\n')
    response=dict(detectors=[dict(theta_min_deg=35.,theta_max_deg=65.,efficiency=.3,order=12,phi_order=24,
        energy_mev=[.05,.15,.3,.6],efficiency_curve=[.9,.8,.7,.6])],particle_phi_order=8,boost=True)
    transitions=[dict(upper=3,lower=2,branch=1.,alpha=0.,multipolarity=2),dict(upper=2,lower=1,branch=1.,alpha=.02,multipolarity=2)]
    data=pd.DataFrame(dict(angle_min_deg=[70.,100.],angle_max_deg=[72.,102.],value=[0.,0.],uncertainty=[1.,1.],efficiency=[.8,.8]))
    edges=tuple(Transition(e['upper']-1,e['lower']-1,e['branch'],e['alpha'],e['multipolarity']) for e in transitions)
    exposure=Exposure(beam_per_second=1e5,days=1.,thickness=2.,azimuth_fraction=1.)
    example=Experiment(data,kind='angular_gamma_counts',transitions=edges,photon_transition=1,gamma_response=GammaResponse.from_dict(response),angular_step=1.,exposure=exposure)
    data['value']=example.predict(primary);data['uncertainty']=.05*data.value
    (out/'synthetic_lab_gamma.json').write_text(json.dumps(dict(
        description='SYNTHETIC, not measured: upload synthetic_rotor.txt first and switch polarization OFF; pure E2 feeding with intrinsic lab gamma response.',
        parameters=[dict(kind='element',index=1)],bounds=[[.1],[2.]],starts=[[elements[0].value*.95]],max_nfev=50,
        experiments=[dict(kind='angular_gamma_counts',transitions=transitions,photon_transition=2,gamma_response=response,
            angular_step=1.,likelihood='gaussian',normalization_sigma=.03,exposure=asdict(exposure),data=data.to_dict('records'))]),indent=2)+'\n')
    mesh=GammaMesh.annulus(35.,65.,phi_min_deg=0.,phi_max_deg=45.,efficiency=.3,order=4,phi_order=4)
    pd.DataFrame(dict(theta_deg=np.rad2deg(np.arccos(mesh.directions[:,2])),
        phi_deg=np.mod(np.rad2deg(np.arctan2(mesh.directions[:,1],mesh.directions[:,0])),360),
        weight_sr=mesh.weights_sr,intrinsic_efficiency=mesh.intrinsic_efficiency)).to_csv(out/'gamma_mesh.csv',index=False)


if __name__=='__main__':main()
