"""Sensitivity, reproducible ensembles and joint likelihood inference.

No solver approximations or interpolation surrogates are introduced here.
"""
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from .workflow import calculate
from .measurements import compare_measurements, Exposure


class ZeroPoissonPredictionError(ValueError):
    """Positive observed count has a model mean exactly zero."""


@dataclass(frozen=True)
class Parameter:
    kind: str
    index: int = 0

    def __post_init__(self):
        if self.kind not in ('element','energy_lab','dipole_strength') or not isinstance(self.index,int) or self.index < 0:
            raise ValueError('Unknown parameter kind or invalid zero-based element index.')

    def get(self, reaction):
        if self.kind == 'element':
            return reaction.elements[self.index].value
        if self.kind in ('energy_lab', 'dipole_strength'):
            return getattr(reaction, self.kind)
        raise ValueError('Unknown research parameter.')

    def set(self, reaction, value):
        if not np.isfinite(value):
            raise ValueError('Parameter values must be finite.')
        if self.kind == 'element':
            elements = list(reaction.elements)
            elements[self.index] = replace(elements[self.index], value=float(value))
            return replace(reaction, elements=tuple(elements))
        if self.kind in ('energy_lab', 'dipole_strength'):
            return replace(reaction, **{self.kind: float(value)})
        raise ValueError('Unknown research parameter.')


def apply_parameters(reaction, parameters, values):
    if len(parameters) != len(values) or len(set(parameters)) != len(parameters):
        raise ValueError('Use distinct parameters and one value per parameter.')
    for parameter, value in zip(parameters, values):
        reaction = parameter.set(reaction, value)
    return reaction


def sensitivity(reaction, angles, parameters, steps, settings=None, **workflow):
    """Central differences of cross sections; compare h and h/2 for convergence."""
    if len(parameters) != len(steps) or not len(parameters):
        raise ValueError('Supply a positive step for every parameter.')
    base = calculate(reaction, angles, settings, **workflow)
    derivatives, errors = [], []
    for parameter, step in zip(parameters, steps):
        if not np.isfinite(step) or step <= 0:
            raise ValueError('Difference steps must be finite and positive.')
        value = parameter.get(reaction)
        def difference(h):
            plus = calculate(parameter.set(reaction, value+h), angles, settings, **workflow)
            minus = calculate(parameter.set(reaction, value-h), angles, settings, **workflow)
            return (plus.cross_sections-minus.cross_sections)/(2*h)
        coarse, fine = difference(step), difference(step/2)
        derivatives.append(fine)
        errors.append(abs(fine-coarse))
    return base, np.stack(derivatives, axis=-1), np.stack(errors, axis=-1)


def covariance_matrix(covariance, size):
    """Validate symmetry and PSD in dimensionless correlation coordinates.

    An absolute matrix tolerance is unsafe for tiny variances or parameters
    with very different units. Zero-variance rows must have zero covariance.
    """
    cov = np.asarray(covariance, float)
    if size < 1 or cov.shape != (size, size) or not np.all(np.isfinite(cov)):
        raise ValueError('Covariance must be finite, symmetric and match the parameters.')
    if not np.allclose(cov,cov.T,atol=0.,rtol=1e-10):
        raise ValueError('Covariance must be finite, symmetric and match the parameters.')
    diagonal = np.diag(cov)
    if np.any(diagonal < 0) or np.any(cov[diagonal == 0] != 0):
        raise ValueError('Covariance must be positive semidefinite.')
    cov = cov/2+cov.T/2
    sigma = np.sqrt(diagonal)
    sigma = np.where(sigma > 0,sigma,1.)
    correlation = cov/sigma[:,None]/sigma[None,:]
    if np.min(np.linalg.eigvalsh(correlation)) < -1e-12:
        raise ValueError('Covariance must be positive semidefinite.')
    return cov


def ensemble(reaction, angles, parameters, covariance, samples=100, seed=2026, settings=None, **workflow):
    """Gaussian input propagation; invalid draws fail explicitly, never disappear."""
    if not isinstance(samples, int) or not 10 <= samples <= 10000:
        raise ValueError('Use 10–10000 ensemble samples.')
    cov = covariance_matrix(covariance, len(parameters))
    draws = np.random.default_rng(seed).multivariate_normal([p.get(reaction) for p in parameters], cov, samples)
    values = []
    for i, draw in enumerate(draws):
        try:
            local = apply_parameters(reaction, parameters, draw)
            values.append(calculate(local, angles, settings, **workflow).cross_sections)
        except ValueError as error:
            raise ValueError(f'Ensemble draw {i+1} is outside the physical input domain; use a suitable bounded input distribution: {error}') from error
    values = np.asarray(values)
    return draws, values, np.quantile(values, [.025, .16, .5, .84, .975], axis=0)


@dataclass
class Experiment:
    data: pd.DataFrame
    kind: str = 'cross_section'
    frame: str = 'CM'
    energy_lab: float | None = None
    exposure: Exposure | None = None
    stopping: object = None
    order: int = 6
    angular_step: float = 1.
    likelihood: str = 'gaussian'
    normalization_sigma: float | None = None
    # Optional full data covariance, for Gaussian observations only.
    covariance: object = None
    reaction_overrides: dict | None = None
    transitions: tuple = ()
    photon_transition: int = 0
    detected_particle: str = 'projectile'
    particle_acceptance: tuple | None = None
    particle_energy_min_mev: float = 0.

    def _compare(self,reaction,data,kind,settings):
        if self.detected_particle != 'projectile' or self.particle_acceptance is not None or self.particle_energy_min_mev:
            from .acceptance import compare_particle_acceptance
            return compare_particle_acceptance(reaction,data,kind,self.frame,settings,self.stopping,
                self.exposure,self.order,self.angular_step,self.detected_particle,self.particle_acceptance,self.particle_energy_min_mev)
        return compare_measurements(reaction,data,kind,self.frame,settings,self.stopping,
                                    self.exposure,self.order,self.angular_step)

    def predict(self, reaction, settings=None):
        if self.reaction_overrides:
            allowed = {'projectile_z','projectile_a','target_z','target_a'}
            if not set(self.reaction_overrides) <= allowed:
                raise ValueError('Only collision-nucleus overrides are permitted.')
            for suffix in ('z','a'):
                key = reaction.excitation+'_'+suffix
                if self.reaction_overrides.get(key,getattr(reaction,key)) != getattr(reaction,key):
                    raise ValueError('Joint experiments must retain the same excited nucleus.')
            reaction = replace(reaction, **self.reaction_overrides)
        if self.energy_lab is not None:
            reaction = reaction.at_energy(self.energy_lab)
        if self.kind in ('strength', 'lifetime_ps', 'quadrupole'):
            from .shapes import reduced
            from .decay import decay_rates
            from .literature import spectroscopic_quadrupole
            values = []
            for row in self.data.itertuples():
                if not np.isfinite(row.level) or row.level != int(row.level) or not 1 <= row.level <= len(reaction.levels):
                    raise ValueError('External constraints require an existing integer level index.')
                level = int(row.level)-1
                if self.kind == 'strength':
                    if row.lower != int(row.lower) or not 1 <= row.lower <= len(reaction.levels) or row.lam not in (1,2,3,4):
                        raise ValueError('Strength constraints require a valid lower level and E1–E4 multipolarity.')
                    values.append(reduced(reaction,level,int(row.lower)-1,int(row.lam))**2/(2*reaction.levels[level].spin+1))
                elif self.kind == 'quadrupole':
                    values.append(spectroscopic_quadrupole(reaction.levels[level].spin,reduced(reaction,level,level)))
                else:
                    rates = decay_rates(reaction, {(e.upper,e.lower):e.alpha for e in self.transitions})
                    total = rates.loc[rates.upper == level+1,'total_rate_s'].sum()
                    if total <= 0:
                        raise ValueError('Lifetime constraint needs an outgoing decay rate.')
                    values.append(1e12/total)
            return np.asarray(values)
        if self.kind == 'cascade_counts':
            from .decay import cascade, validate_network
            validate_network(reaction,self.transitions)
            if not 0 <= self.photon_transition < len(self.transitions):
                raise ValueError('Select a decay transition in the supplied network.')
            if 'gamma_efficiency' not in self.data or np.any(~np.isfinite(self.data.gamma_efficiency)) or not self.data.gamma_efficiency.between(0,1).all():
                raise ValueError('Cascade photon efficiency must be a fraction in [0,1].')
            prediction = np.zeros(len(self.data))
            for level in range(1,len(reaction.levels)):
                initial = np.eye(len(reaction.levels))[level]
                weight = cascade(reaction,initial,self.transitions)[1][self.photon_transition]
                if weight:
                    data = self.data.copy()
                    data['level'] = level+1
                    partial = self._compare(reaction,data,'particle_counts',settings).predicted.to_numpy()
                    prediction += weight*partial*self.data.gamma_efficiency.to_numpy()
            return prediction
        return self._compare(reaction,self.data,self.kind,settings).predicted.to_numpy()


def likelihood_residual(observed, predicted, likelihood, uncertainty=None, covariance=None):
    y, mu = np.asarray(observed, float), np.asarray(predicted, float)
    if y.shape != mu.shape or np.any(~np.isfinite(y)) or np.any(~np.isfinite(mu)) or (likelihood == 'poisson' and np.any(mu < 0)):
        raise ValueError('Likelihood predictions must be finite and nonnegative.')
    if likelihood == 'poisson':
        if np.any(y < 0) or np.any(y != np.floor(y)):
            raise ValueError('Poisson data must be raw nonnegative integer counts.')
        if np.any((y > 0) & (mu == 0)):
            raise ZeroPoissonPredictionError('Positive counts have zero predicted mean; the Poisson likelihood is zero. Choose a nonzero starting prediction.')
        residual = np.asarray(np.sqrt(2.)*np.sqrt(mu))
        positive = y > 0
        yp, mp = y[positive], mu[positive]
        delta = (mp-yp)/yp
        close = abs(delta) < 1e-3
        core = np.empty_like(yp)
        # delta-log1p(delta) loses its leading digits close to zero.
        d = delta[close]
        core[close] = yp[close]*d*d*(.5+d*(-1/3+d*(.25+d*(-.2+d/6))))
        middle = (~close) & (delta > -.99)
        core[middle] = yp[middle]*(delta[middle]-np.log1p(delta[middle]))
        far = (~close) & (~middle)
        core[far] = mp[far]-yp[far]+yp[far]*(np.log(yp[far])-np.log(mp[far]))
        residual[positive] = np.sign(delta)*np.sqrt(2.)*np.sqrt(np.maximum(core,0.))
        return residual
    if likelihood != 'gaussian':
        raise ValueError('Choose gaussian or poisson likelihood.')
    if covariance is not None:
        cov = covariance_matrix(covariance, len(y))
        try:
            return np.linalg.solve(np.linalg.cholesky(cov), mu-y)
        except np.linalg.LinAlgError as error:
            raise ValueError('Observation covariance must be positive definite.') from error
    sigma = np.asarray(uncertainty, float)
    if sigma.shape != y.shape or np.any(~np.isfinite(sigma)) or np.any(sigma <= 0):
        raise ValueError('Every Gaussian observation requires a positive uncertainty.')
    return (mu-y)/sigma


def _fit_objective(reaction,parameters,experiments,settings):
    nuisances = [i for i,e in enumerate(experiments) if e.normalization_sigma is not None]
    for e in experiments:
        if e.likelihood == 'poisson' and not e.kind.endswith('counts'):
            raise ValueError('Poisson likelihood requires raw count observables.')
        if e.normalization_sigma is not None and (not np.isfinite(e.normalization_sigma) or e.normalization_sigma <= 0):
            raise ValueError('Normalization log-scale uncertainty must be positive.')
    n = len(parameters)
    def residual(values):
        local = apply_parameters(reaction, parameters, values[:n])
        terms = []
        for i, experiment in enumerate(experiments):
            prediction = experiment.predict(local, settings)
            if i in nuisances:
                eta = values[n+nuisances.index(i)]
                prediction = prediction*np.exp(eta)
                terms.append(np.array([eta/experiment.normalization_sigma]))
            terms.append(likelihood_residual(experiment.data.value, prediction, experiment.likelihood,
                         experiment.data.get('uncertainty'), experiment.covariance))
        return np.concatenate(terms)
    return residual,nuisances


def joint_fit(reaction, parameters, experiments, bounds, starts=None, settings=None, max_nfev=100):
    """Multi-start bounded fit with log-normal multiplicative nuisance scales.

    Local covariance is (JᵀJ)^-1 without reduced-chi² rescaling. Singular fits
    return no covariance. Multiple minima remain available to the caller.
    """
    if not parameters or not experiments or len(set(parameters)) != len(parameters):
        raise ValueError('Specify distinct fit parameters and at least one experiment.')
    if any(p.kind == 'energy_lab' for p in parameters) and any(e.energy_lab is not None for e in experiments):
        raise ValueError('A fitted common energy cannot be overridden by experiment energies.')
    n = len(parameters)
    lo, hi = np.asarray(bounds[0], float), np.asarray(bounds[1], float)
    if lo.shape != (n,) or hi.shape != (n,) or np.any(np.isnan(lo)) or np.any(np.isnan(hi)) or np.any(lo >= hi):
        raise ValueError('Supply ordered lower and upper bounds for every parameter.')
    residual,nuisances = _fit_objective(reaction,parameters,experiments,settings)
    starts = starts if starts is not None else [[p.get(reaction) for p in parameters]]
    solutions = []
    for start in starts:
        if len(start) != n:
            raise ValueError('Every starting point must match the fit parameters.')
        solutions.append(least_squares(residual, np.r_[start, np.zeros(len(nuisances))],
                         bounds=(np.r_[lo, np.full(len(nuisances), -20.)], np.r_[hi, np.full(len(nuisances), 20.)]),
                         max_nfev=max_nfev, diff_step=1e-4, xtol=1e-8, ftol=1e-8, gtol=1e-8))
    best = min(solutions, key=lambda s: s.cost)
    rank = np.linalg.matrix_rank(best.jac)
    cov = None
    if best.success and rank == len(best.x) and np.linalg.cond(best.jac) < 1e8 and not np.any(best.active_mask):
        # Avoid squaring the condition number by forming/inverting J.T@J.
        _, singular_values, vh = np.linalg.svd(best.jac,full_matrices=False)
        cov = (vh.T/singular_values**2)@vh
    return dict(values=best.x, covariance=cov, residuals=best.fun, objective=2*best.cost,
                success=best.success, message=best.message, rank=int(rank),
                active_bounds=best.active_mask, solutions=[dict(values=s.x.tolist(), objective=2*s.cost,
                success=s.success) for s in solutions], nuisance_experiments=nuisances,
                dof=len(best.fun)-len(best.x))


def profile_fit(reaction, parameters, experiments, bounds, parameter_index, grid, settings=None, max_nfev=100):
    """Refit remaining parameters and nuisance scales; also supports one parameter."""
    if not 0 <= parameter_index < len(parameters):
        raise ValueError('Invalid profile parameter.')
    if len(bounds) != 2 or any(len(row)!=len(parameters) for row in bounds):
        raise ValueError('Profile bounds must match the parameters.')
    rows = []
    free = [i for i in range(len(parameters)) if i != parameter_index]
    for value in grid:
        if not np.isfinite(value) or not bounds[0][parameter_index] <= value <= bounds[1][parameter_index]:
            raise ValueError('Profile grid values must lie inside the parameter bounds.')
        local = parameters[parameter_index].set(reaction,value)
        compatible=True
        try:
            if free:
                result = joint_fit(local,[parameters[i] for i in free],experiments,
                                   ([bounds[0][i] for i in free],[bounds[1][i] for i in free]),settings=settings,max_nfev=max_nfev)
                objective,success = result['objective'],result['success']
            else:
                residual,nuisances = _fit_objective(local,[],experiments,settings)
                if nuisances:
                    fit = least_squares(residual,np.zeros(len(nuisances)),bounds=(-20.,20.),
                                        max_nfev=max_nfev,xtol=1e-10,ftol=1e-10,gtol=1e-10)
                    objective,success = 2*fit.cost,bool(fit.success and not np.any(fit.active_mask))
                else:
                    values=residual(np.empty(0))
                    objective,success = float(values@values),True
        except ZeroPoissonPredictionError:
            if free:
                raise
            objective,success,compatible=float('inf'),True,False
        rows.append(dict(value=value,objective=objective,success=success,compatible=compatible))
    return pd.DataFrame(rows)


def information_matrix(jacobian, uncertainties, normalization_prediction=None, normalization_sigma=None):
    """Gaussian Fisher information, profiling one shared log-normalization nuisance."""
    jacobian, sigma = np.asarray(jacobian,float), np.asarray(uncertainties,float)
    if jacobian.ndim != 2 or sigma.shape != (len(jacobian),) or np.any(sigma <= 0) or not np.all(np.isfinite(jacobian)) or not np.all(np.isfinite(sigma)):
        raise ValueError('Information needs finite derivatives and positive observation uncertainties.')
    j = jacobian/sigma[:,None]
    info = j.T@j
    if normalization_prediction is not None:
        v = np.asarray(normalization_prediction,float)/sigma
        prior = 0. if normalization_sigma is None else 1/normalization_sigma**2
        denominator = v@v+prior
        if denominator > 0:
            coupling = j.T@v
            info -= np.outer(coupling,coupling)/denominator
    return info


def systematic_ensemble(reaction, angles, parameters, covariance, samples=100, seed=2026, settings=None,
                        stopping=None, thickness=0., order=6, thickness_sigma=0., stopping_scale_sigma=0.):
    """Independent log-normal thickness/stopping scales plus correlated Gaussian nuclear inputs.

    Scale sigmas are standard deviations of log(scale); central scales are medians.
    """
    from .stopping import StoppingTable
    if min(thickness_sigma,stopping_scale_sigma) < 0 or not np.isfinite(thickness_sigma+stopping_scale_sigma):
        raise ValueError('Systematic log-scale uncertainties must be finite and nonnegative.')
    if stopping_scale_sigma and stopping is None:
        raise ValueError('A stopping scale uncertainty requires a stopping table.')
    if not isinstance(samples,int) or not 10 <= samples <= 10000:
        raise ValueError('Use 10–10000 ensemble samples.')
    cov = covariance_matrix(covariance,len(parameters))
    rng = np.random.default_rng(seed)
    draws = rng.multivariate_normal([p.get(reaction) for p in parameters],cov,samples)
    scales = np.exp(rng.normal(size=(samples,2))*[thickness_sigma,stopping_scale_sigma])
    predictions = []
    for draw,scale in zip(draws,scales):
        local_stopping = StoppingTable(stopping.energy,stopping.stopping*scale[1]) if stopping else None
        predictions.append(calculate(apply_parameters(reaction,parameters,draw),angles,settings,local_stopping,
                                     thickness*scale[0],order).cross_sections)
    predictions = np.asarray(predictions)
    return draws,scales,predictions,np.quantile(predictions,[.025,.16,.5,.84,.975],axis=0)
