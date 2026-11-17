"""Named nuclear models for simultaneous projectile/target normalization.

Each nucleus is excited with the existing single-partner solver. This is not a
product-space mutual-excitation calculation. Model and normalization choices
are explicit in each dataset; target structure can be constrained in the fit.
"""
from dataclasses import dataclass
from .model import Reaction,Level,MatrixElement


@dataclass(frozen=True)
class JointModel:
    models: dict[str,Reaction]

    def __post_init__(self):
        if 'primary' not in self.models or any(not isinstance(k,str) or not k.strip() or not isinstance(v,Reaction) for k,v in self.models.items()):
            raise ValueError('Joint models need named Reaction objects including primary.')
        object.__setattr__(self,'models',dict(self.models))

    def selected(self,name=None):
        key=name or 'primary'
        if key not in self.models: raise ValueError('An experiment or parameter selects an unknown nuclear model: '+key)
        return self.models[key]

    def updated(self,name,reaction):
        key=name or 'primary';self.selected(key)
        return JointModel({**self.models,key:reaction})


def configured_model(config,primary):
    from .research_io import one_based
    models={'primary':primary}
    additional=config.get('models',{})
    if not isinstance(additional,dict): raise ValueError('Additional models must be a JSON object with named reaction definitions.')
    for name,definition in additional.items():
        if name=='primary': raise ValueError('The primary model is supplied by the sidebar; use another name for an additional nucleus.')
        definition=dict(definition)
        definition['levels']=tuple(Level(**x) for x in definition['levels'])
        definition['elements']=tuple(MatrixElement(one_based(x['initial']),one_based(x['final']),x['value'],x.get('multipolarity',2)) for x in definition['elements'])
        models[name]=Reaction(**definition)
    return JointModel(models) if len(models)>1 else primary
