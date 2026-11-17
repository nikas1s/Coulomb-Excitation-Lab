"""Nonlinear inference checks against the analytic sudden two-state limit.

Counts are ideal Poisson-thinned population observations with a known exposure,
not a finite detector simulation. No interpolated/surrogate solver is used.
"""
from collections import Counter
from dataclasses import replace
import math
import numpy as np
import pandas as pd
from scipy.stats import binomtest,norm,chi2,poisson
from coulex import Reaction,Level,MatrixElement,CoupledChannels,SolverSettings
from coulex.research import Experiment,Parameter,joint_fit,profile_fit
from coulex.literature import strength_parameter


def setup():
    r=Reaction('sudden two-state inference reference',8,16,28,58,30.,
               (Level(0,0),Level(2,0)),(MatrixElement(0,1,1.),),excitation='target',dipole_strength=0.)
    k=strength_parameter(r,1,2,1.)
    truth=math.pi/6/k
    return replace(r,elements=(MatrixElement(0,1,truth),)),Parameter('element',0),k


def coverage_interval(hits,trials,nominal):
    ci=binomtest(hits,trials).proportion_ci(confidence_level=.99,method='exact')
    return dict(hits=int(hits),trials=trials,observed=hits/trials,nominal=nominal,
                binomial_99_interval=[ci.low,ci.high],consistent=bool(ci.low<=nominal<=ci.high),
                not_significantly_below_nominal=bool(ci.high>=nominal))


class PopulationExperiment(Experiment):
    """Direct ODE prediction, cached only at identical parameter inputs."""
    def __init__(self,data,cache,exposure=1.,likelihood='gaussian'):
        super().__init__(data,kind='ideal_population_counts' if likelihood=='poisson' else 'probability',likelihood=likelihood)
        self.cache=cache
        self.exposure=exposure

    def predict(self,reaction,settings=None):
        value=reaction.elements[0].value
        if value not in self.cache:
            self.cache[value]=CoupledChannels(reaction).solve(180.,settings).probabilities[1]
        return np.array([self.exposure*self.cache[value]])


def nonlinear_coverage(gaussian_trials=100,count_trials=500,seed=447):
    if gaussian_trials<100 or count_trials<100:
        raise ValueError('Use at least 100 trials in each coverage experiment.')
    r,p,k=setup();truth=p.get(r); bounds=([0.],[math.pi/(2*k)])
    settings=SolverSettings(rtol=1e-10,atol=1e-13,extra_omega=.5)
    rng=np.random.default_rng(seed);cache={};sigma=.04
    hits={.68:0,.95:0};failures=0;boundary=0;max_estimator_error=0.;max_variance_relative_error=0.
    for i,y in enumerate(rng.normal(.25,sigma,gaussian_trials)):
        data=pd.DataFrame(dict(value=[y],uncertainty=[sigma]))
        experiment=PopulationExperiment(data,cache)
        fit=joint_fit(r,[p],[experiment],bounds,settings=settings,max_nfev=40)
        if not fit['success'] or fit['covariance'] is None:
            failures+=1;continue
        estimate=float(fit['values'][0]); variance=fit['covariance'][0,0]
        if not 0<y<1:
            raise ValueError('The regular Gaussian study encountered a boundary observation; a separate boundary design is required.')
        expected=math.asin(math.sqrt(y))/k
        exact_variance=(sigma/(k*math.sin(2*k*expected)))**2
        max_estimator_error=max(max_estimator_error,abs(estimate-expected))
        max_variance_relative_error=max(max_variance_relative_error,abs(variance/exact_variance-1))
        for nominal in hits:
            hits[nominal]+=bool(abs(estimate-truth)<=norm.ppf((1+nominal)/2)*math.sqrt(variance))
        if (i+1)%25==0: print(f'Nonlinear Gaussian trials: {i+1}/{gaussian_trials}',flush=True)
    gaussian={str(c):coverage_interval(n,gaussian_trials,c) for c,n in hits.items()}
    # Repeated identical observations have identical deterministic fits. Fit
    # each integer observation once, preserving all Monte Carlo frequencies.
    exposure=12.;mean=exposure*.25
    observations=rng.poisson(mean,count_trials); frequencies=Counter(map(int,observations))
    poisson_rows=[];wald_hits=0;wald_available=0;garwood_hits=0;profile_error=0.;fit_failures=0
    for n,frequency in sorted(frequencies.items()):
        e=PopulationExperiment(pd.DataFrame(dict(value=[n])),cache,exposure,'poisson')
        fit=joint_fit(r,[p],[e],bounds,settings=settings,max_nfev=80)
        expected=math.asin(math.sqrt(min(n/exposure,1.)))/k
        estimate=float(fit['values'][0])
        if not fit['success']: fit_failures+=frequency
        cov=fit['covariance']
        if cov is not None:
            wald_available+=frequency
            wald_hits+=frequency*bool(abs(estimate-truth)<=norm.ppf(.975)*math.sqrt(cov[0,0]))
        # Exact central Poisson interval, monotonically transformed on the
        # specified first Rabi branch; clipping is to a declared parameter domain.
        lo=0. if n==0 else .5*chi2.ppf(.025,2*n)
        hi=.5*chi2.ppf(.975,2*(n+1))
        lower=math.asin(math.sqrt(min(lo/exposure,1.)))/k
        upper=math.asin(math.sqrt(min(hi/exposure,1.)))/k
        garwood_hits+=frequency*bool(lower<=truth<=upper)
        grid=[truth*.6,truth,truth*1.5]
        profile=profile_fit(r,[p],[e],bounds,0,grid,settings=settings)
        exact=2*(poisson.logpmf(n,n)-poisson.logpmf(n,exposure*np.sin(k*np.asarray(grid))**2))
        discrepancy=float(np.max(abs(profile.objective.to_numpy()-exact)))
        # Profile returns absolute deviance, so the saturated maximum is zero
        # whenever n is reachable (all current seeded observations are <= 12).
        profile_error=max(profile_error,discrepancy)
        poisson_rows.append(dict(count=n,frequency=frequency,estimate=estimate,analytic_mle=expected,
            success=bool(fit['success']),covariance_available=cov is not None,exact_interval=[lower,upper],
            profile_max_difference=discrepancy))
    count_coverage=coverage_interval(garwood_hits,count_trials,.95)
    exact_coverage=0.
    for n in range(int(poisson.ppf(1-1e-13,mean))+1):
        lo=0. if n==0 else .5*chi2.ppf(.025,2*n)
        hi=.5*chi2.ppf(.975,2*(n+1))
        if lo<=mean<=hi: exact_coverage+=poisson.pmf(n,mean)
    count_coverage['analytic_discrete_coverage']=float(exact_coverage)
    low,high=count_coverage['binomial_99_interval']
    count_coverage['matches_analytic_coverage']=bool(low<=exact_coverage<=high)
    max_count_estimator_error=max(abs(row['estimate']-row['analytic_mle']) for row in poisson_rows)
    return dict(seed=seed,gaussian_trials=gaussian_trials,count_trials=count_trials,
        gaussian=dict(intervals=gaussian,failed=failures,max_estimator_error=max_estimator_error,
            max_variance_relative_error=max_variance_relative_error),
        counts=dict(mean=mean,known_exposure=exposure,rows=poisson_rows,failed=fit_failures,
            exact_transformed_interval_coverage=count_coverage,max_estimator_error=max_count_estimator_error,
            wald_interval_hits=wald_hits,wald_covariance_available=wald_available,
            wald_coverage_over_all_trials=wald_hits/count_trials,profile_max_difference=profile_error),
        direct_solver_evaluations=len(cache),
        passed=bool(not failures and not fit_failures and max_estimator_error<1e-4 and max_variance_relative_error<1e-3
                    and all(v['consistent'] for v in gaussian.values()) and count_coverage['not_significantly_below_nominal']
                    and profile_error<1e-3 and count_coverage['matches_analytic_coverage'] and max_count_estimator_error<1e-4),
        scope='Actual coupled-channel ODE in degenerate sudden limit, first monotone Rabi branch; no fitted normalization or finite detector response. Exact Poisson intervals are a qualification reference, not a general UI interval method.')
