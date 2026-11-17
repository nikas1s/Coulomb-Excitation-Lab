"""Seeded nondegenerate coupled-channel fits with normalization calibration.

No interpolated model, surrogate or renormalized probabilities. This is a scoped
Gaussian study, not coverage evidence for every nonlinear/Poisson detector fit.
Run: python validation/multilevel_coverage.py --trials 100
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import pandas as pd
from scipy.stats import norm,binomtest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from coulex import CoupledChannels,SolverSettings
from coulex.research import Parameter,Experiment,joint_fit
from coulex.literature import spectroscopic_quadrupole
from validation.gosia_points import cases


def run(trials=100,seed=9073):
    if trials<100: raise ValueError('Use at least 100 coverage trials.')
    reaction=list(cases())[4]
    settings=SolverSettings(rtol=1e-8,atol=1e-11)
    parameters=[Parameter('element',0),Parameter('element',1)]
    truth=np.array([p.get(reaction) for p in parameters])
    template=pd.DataFrame(dict(angle_deg=[50.,90.,135.,135.],level=[2,2,2,3],value=[0.]*4,uncertainty=[1.]*4))
    mean=Experiment(template).predict(reaction,settings)
    sigma=.03*mean;calibration_sigma=.05;moment_sigma=.06
    moment=spectroscopic_quadrupole(2,truth[1]);rng=np.random.default_rng(seed)
    records=[];hits={str(n):np.zeros(3,int) for n in (.68,.95)};failures=0;boundary=0;pulls=[]
    for trial in range(trials):
        # A fresh independent external calibration is measured in each trial.
        # Correcting by its measured scale leaves a true eta = -log(calibration).
        calibration=rng.normal(0,calibration_sigma)
        data=template.copy();data['value']=rng.normal(mean,sigma)*np.exp(-calibration)
        data['uncertainty']=sigma*np.exp(-calibration)
        external=Experiment(pd.DataFrame(dict(level=[2],value=[rng.normal(moment,moment_sigma)],
            uncertainty=[moment_sigma])),kind='quadrupole')
        experiments=[Experiment(data,normalization_sigma=calibration_sigma),external]
        fit=joint_fit(reaction,parameters,experiments,([.15,-1.],[.8,1.]),
            starts=[[.35,-.15],[.5,.15]],settings=settings,max_nfev=60)
        true=np.r_[truth,-calibration]
        valid=bool(fit['success'] and fit['covariance'] is not None)
        boundary+=int(np.any(fit['active_bounds']))
        record=dict(trial=trial,success=bool(fit['success']),covariance_available=fit['covariance'] is not None,
            objective=float(fit['objective']),values=fit['values'].tolist(),truth=true.tolist(),
            active_bounds=fit['active_bounds'].tolist(),solutions=fit['solutions'])
        if valid:
            sd=np.sqrt(np.diag(fit['covariance']));pull=(fit['values']-true)/sd;pulls.append(pull)
            record.update(standard_deviations=sd.tolist(),pulls=pull.tolist())
            for nominal in (.68,.95): hits[str(nominal)]+=abs(pull)<=norm.ppf((1+nominal)/2)
        else: failures+=1
        records.append(record)
        print(f'Fit {trial+1}/{trials}: {"PASS" if valid else "FAIL"}, objective={fit["objective"]:.4g}',flush=True)
    intervals={}
    for nominal,counts in hits.items():
        entries=[]
        for hit in counts:
            ci=binomtest(int(hit),trials).proportion_ci(.99,method='exact')
            entries.append(dict(hits=int(hit),observed=float(hit/trials),binomial_99_interval=[ci.low,ci.high],
                passed=bool(ci.low<=float(nominal)<=ci.high)))
        intervals[nominal]=entries
    pulls=np.asarray(pulls)
    return dict(trials=trials,seed=seed,failed=failures,boundary_fits=boundary,
        parameter_order=['ME(0,2)','ME(2,2)','log_normalization'],
        method='Actual coupled-channel fits, two starts, Gaussian cross sections plus independent Q and log-normalization calibrations; local Wald intervals',
        scope='One target-excited nondegenerate 0+/2+/4+ E2 network, four cross sections and external Q; ideal known errors; no detector-systematic or Poisson coverage claim',
        reaction_title=reaction.title,settings=vars(settings),calibration_sigma=calibration_sigma,
        fractional_data_sigma=.03,moment_sigma=moment_sigma,intervals=intervals,
        pull_mean=np.mean(pulls,axis=0).tolist() if len(pulls) else None,
        pull_sd=np.std(pulls,axis=0,ddof=1).tolist() if len(pulls)>1 else None,records=records,
        passed=bool(not failures and not boundary and all(e['passed'] for group in intervals.values() for e in group)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--trials',type=int,default=100)
    args=parser.parse_args();report=run(args.trials)
    destination=ROOT/'validation/research_qualification/multilevel-coverage.json'
    destination.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print('Coverage:',report['intervals'],flush=True)
    raise SystemExit(0 if report['passed'] else 1)
