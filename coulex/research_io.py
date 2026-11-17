"""Portable JSON configuration for multi-experiment fits (indices are one-based)."""
import json
import pandas as pd
from .research import Parameter, Experiment
from .measurements import Exposure
from .decay import Transition
from .stopping import StoppingTable


def one_based(value):
    import math
    number = float(value)
    if not math.isfinite(number) or number != int(number) or number < 1:
        raise ValueError('JSON indices must be positive one-based integers.')
    return int(number)-1


def load_fit(text):
    config = json.loads(text)
    parameters = [Parameter(p['kind'],one_based(p.get('index',1))) for p in config['parameters']]
    experiments = []
    for item in config['experiments']:
        item = dict(item)
        item['data'] = pd.DataFrame(item['data'])
        if item.get('exposure'):
            item['exposure'] = Exposure(**item['exposure'])
        if item.get('stopping'):
            item['stopping'] = StoppingTable(**item['stopping'])
        item['transitions'] = tuple(Transition(one_based(e['upper']),one_based(e['lower']),e['branch'],e.get('alpha',0.),e.get('multipolarity',2)) for e in item.get('transitions',[]))
        if 'photon_transition' in item:
            item['photon_transition'] = one_based(item['photon_transition'])
        if item.get('reaction_overrides') and not set(item['reaction_overrides']) <= {'projectile_z','projectile_a','target_z','target_a'}:
            raise ValueError('Experiment overrides may only change the collision nuclei.')
        experiments.append(Experiment(**item))
    return config,parameters,experiments


def fit_template(reaction):
    """Illustrative data schema only: values are placeholders, not observations."""
    index = next((i for i,m in enumerate(reaction.elements) if m.initial != m.final and m.value),0)
    me = reaction.elements[index]
    size = max(abs(me.value),.1)
    return json.dumps(dict(parameters=[dict(kind='element',index=index+1)],
        bounds=[[me.value-2*size],[me.value+2*size]],starts=[[me.value],[me.value*.8]],
        experiments=[dict(kind='cross_section',frame='CM',energy_lab=reaction.energy_lab,
            likelihood='gaussian',normalization_sigma=.05,
            data=[dict(angle_deg=a,level=max(me.initial,me.final)+1,value=.01,uncertainty=.001) for a in (60,100,140)])]),indent=2)


def export_json(value):
    """Standards-compliant JSON: nonfinite unavailable values become null."""
    import math
    import numpy as np
    def clean(item):
        if isinstance(item,pd.DataFrame): return clean(item.to_dict('records'))
        if isinstance(item,np.ndarray): return clean(item.tolist())
        if isinstance(item,np.generic): return clean(item.item())
        if isinstance(item,float) and not math.isfinite(item): return None
        if isinstance(item,dict): return {key:clean(val) for key,val in item.items()}
        if isinstance(item,(list,tuple)): return [clean(val) for val in item]
        return item
    return json.dumps(clean(value),indent=2,allow_nan=False)
