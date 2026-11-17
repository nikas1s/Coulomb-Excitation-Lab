"""Research workbench. Every costly job is explicit and tied to its inputs."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from .i18n import t, error_text
from .research import Parameter, sensitivity, systematic_ensemble, joint_fit, profile_fit, information_matrix
from .research_io import load_fit, fit_template, export_json
from .shapes import invariants, invariant_ensemble
from .decay import Transition, cascade, validate_network, decay_rates, cascade_densities, photon_map, fold_detector
from .solver import CoupledChannels
from .workflow import calculate
from .plots import style


def parameter_label(p,model):
    if p.kind == 'element':
        m=model.elements[p.index]
        return f'E{m.multipolarity}: {m.initial+1} ↔ {m.final+1} [{p.index+1}]'
    return t('Beam energy (total MeV)') if p.kind == 'energy_lab' else t('Polarization strength d (MeV⁻¹)')


def _json(value):
    if isinstance(value,np.ndarray): return value.tolist()
    if isinstance(value,np.generic): return value.item()
    if isinstance(value,pd.DataFrame): return value.to_dict('records')
    raise TypeError(type(value).__name__)


def job(key, payload, action):
    signature=hashlib.sha256(json.dumps(payload,default=_json,sort_keys=True).encode()).hexdigest()
    if st.button(t('Run research calculation'),key=f'run_{key}',type='primary'):
        try:
            with st.spinner(t('Calculating research observables…')):
                value=action()
            st.session_state[key]=(signature,value)
        except (ValueError,RuntimeError,KeyError,TypeError,IndexError,np.linalg.LinAlgError) as error:
            st.error(error_text(error))
    stored=st.session_state.get(key)
    if stored and stored[0] != signature:
        st.info(t('Research inputs changed. Run again to update this result.'))
    if stored and stored[0] == signature:
        st.download_button(t('Download research results (JSON)'),export_json(stored[1]),f'{key}.json','application/json',key=f'dl_{key}')
        return stored[1]


def render(model,settings,stopping=None,thickness=0.,order=6):
    st.subheader(t('Research workbench'))
    if model is None:
        st.info(t('Define a reaction in the sidebar to see its level scheme.'))
        return
    st.caption(t('Research tools use the current sidebar model. Each calculation records its own inputs; validate numerical and model-space convergence before interpreting results.'))
    root=Path(__file__).resolve().parents[1]
    with st.expander(t('Research guide and examples')):
        st.markdown(t('Read docs/RESEARCH.md for equations, upload schemas, assumptions and validation. Synthetic examples are teaching data, not experimental measurements.'))
        for path in sorted((root/'examples/research').glob('*')):
            if path.suffix in ('.json','.csv','.txt'):
                st.download_button(path.name,path.read_bytes(),path.name,key='example_'+path.name)
    modes=['Sensitivity and design','Uncertainty bands','Nuclear shape invariants','Joint parameter fitting','Gamma cascades and correlations','Octupole and model comparisons']
    mode=st.selectbox(t('Research task'),modes,format_func={v:t(v) for v in modes}.__getitem__,key='research_mode')
    payload=dict(model=asdict(model),settings=asdict(settings),stopping=dict(energy=stopping.energy.tolist(),stopping=stopping.stopping.tolist()) if stopping else None,thickness=thickness,order=order)
    pars=[Parameter('element',i) for i in range(len(model.elements))]+[Parameter('energy_lab'),Parameter('dipole_strength')]
    workflow=dict(stopping=stopping,thickness=thickness,order=order)
    if mode in modes[:2]:
        selected=st.multiselect(t('Variable parameters'),list(range(len(pars))),default=[0] if model.elements else [],format_func={i:parameter_label(p,model) for i,p in enumerate(pars)}.__getitem__)
        parameters=[pars[i] for i in selected]
        a,b,c=st.columns(3)
        amin=a.number_input(t('Research minimum CM angle (°)'),min_value=.1,max_value=179.,value=30.)
        amax=b.number_input(t('Research maximum CM angle (°)'),min_value=1.,max_value=180.,value=150.)
        count=c.number_input(t('Research angle samples'),min_value=2,max_value=100,value=7)
        if amin >= amax or not parameters:
            st.info(t('Select parameters and an increasing angle range.')); return
        angles=np.linspace(amin,amax,count)
        table=pd.DataFrame([dict(parameter=parameter_label(p,model),value=p.get(model),step=max(abs(p.get(model))*.02,.0001),sigma=max(abs(p.get(model))*.05,.0001)) for p in parameters])
        table=st.data_editor(table,disabled=['parameter','value'],hide_index=True,key='research_parameters_'+hashlib.sha256(json.dumps([asdict(model),selected],sort_keys=True).encode()).hexdigest()[:12])
        payload.update(parameters=[asdict(p) for p in parameters],angles=angles.tolist(),table=table.to_dict('records'))
        level=st.selectbox(t('Observed level'),range(len(model.levels)),index=min(1,len(model.levels)-1),format_func=lambda i:str(i+1))
        if mode == modes[0]:
            energy_text=st.text_input(t('Beam energies to compare (MeV, comma separated)'),value=str(model.energy_lab))
            payload['energies']=energy_text
            def run():
                energies=[float(x) for x in energy_text.split(',')]
                if not 1 <= len(energies) <= 12: raise ValueError('Use one to twelve beam energies.')
                rows=[]
                for energy in energies:
                    base,jac,error=sensitivity(model.at_energy(energy),angles,parameters,table.step.to_numpy(),settings,**workflow)
                    for a,theta in enumerate(angles):
                        for l in range(len(model.levels)):
                            for k,p in enumerate(parameters):
                                rows.append(dict(energy_mev=energy,angle=theta,level=l+1,parameter=parameter_label(p,model),cross_section=base.cross_sections[a,l],derivative=jac[a,l,k],step_difference=error[a,l,k]))
                return dict(inputs=payload,rows=rows)
            result=job('research_sensitivity',payload,run)
            if result:
                data=pd.DataFrame(result['rows']); data=data[data.level==level+1]
                fig=go.Figure()
                for (energy,p),group in data.groupby(['energy_mev','parameter']):
                    fig.add_scatter(x=group.angle,y=group.derivative,name=f'{energy:g} MeV · {p}')
                st.plotly_chart(style(fig,t('CM angle (°)'),t('Cross-section derivative')))
                st.dataframe(data,hide_index=True)
                heat=data.pivot_table(index='parameter',columns=['energy_mev','angle'],values='derivative')
                st.plotly_chart(go.Figure(go.Heatmap(z=heat.to_numpy(),y=heat.index.tolist(),
                    x=[f'{e:g} MeV / {a:g}°' for e,a in heat.columns],colorscale='RdBu',zmid=0)))
                fraction=st.number_input(t('Assumed fractional cross-section uncertainty'),min_value=.001,max_value=1.,value=.05)
                normalization=st.number_input(t('Shared normalization log-scale uncertainty'),min_value=.001,max_value=1.,value=.05)
                positive=data[data.cross_section>0]
                design=positive.pivot_table(index=['energy_mev','angle'],columns='parameter',values='derivative')
                if not design.empty:
                    predicted=positive.groupby(['energy_mev','angle']).cross_section.first().reindex(design.index).to_numpy()
                    info=information_matrix(design.to_numpy(),fraction*predicted,predicted,normalization)
                    st.dataframe(pd.DataFrame(info,index=design.columns,columns=design.columns))
                    st.download_button(t('Download design information (JSON)'),export_json(dict(inputs=result['inputs'],observed_level=level+1,fractional_uncertainty=fraction,normalization_sigma=normalization,information=info,parameter_order=design.columns.tolist())), 'design_information.json','application/json')
                    st.caption(t('Fisher information assumes independent Gaussian fractional errors and one shared normalization nuisance. Its rank and eigenvalues describe local constraints, not global uniqueness.'))
                st.caption(t('Step difference compares central derivatives at h and h/2. Large differences require a new step or tighter solver settings. Sensitivity alone does not establish identifiability.'))
        else:
            covariance=st.file_uploader(t('Optional covariance CSV (parameter order above)'),type=['csv'],key='research_cov')
            samples=st.number_input(t('Ensemble samples'),min_value=10,max_value=2000,value=100)
            seed=st.number_input(t('Random seed'),min_value=0,value=2026)
            ts=st.number_input(t('Target thickness log-scale uncertainty'),min_value=0.,value=0.)
            ss=st.number_input(t('Stopping-power log-scale uncertainty'),min_value=0.,value=0.)
            cov=pd.read_csv(covariance,header=None).to_numpy() if covariance else np.diag(table.sigma.to_numpy()**2)
            payload.update(covariance=cov.tolist(),samples=samples,seed=seed,thickness_sigma=ts,stopping_sigma=ss)
            def run():
                draws,scales,values,q=systematic_ensemble(model,angles,parameters,cov,samples,seed,settings,**workflow,thickness_sigma=ts,stopping_scale_sigma=ss)
                return dict(inputs=payload,draws=draws,systematic_scales=scales,quantiles=q)
            result=job('research_uncertainty',payload,run)
            if result:
                q=np.asarray(result['quantiles'])[:,:,level]
                fig=go.Figure()
                for k,name in ((0,'2.5%'),(4,'97.5%'),(2,'50%')):
                    fig.add_scatter(x=angles,y=q[k],name=name,fill='tonexty' if k==4 else None)
                st.plotly_chart(style(fig,t('CM angle (°)'),t('dσ/dΩ (barn/sr)')))
                st.caption(t('These are propagated input-distribution quantiles, not confidence intervals or a bound on omitted physics. Gaussian draws outside the physical domain cause an explicit error.'))
    elif mode == modes[2]:
        zero=[i for i,l in enumerate(model.levels) if l.spin==0 and l.parity==1]
        if not zero: st.info(t('This invariant implementation requires a 0+ state.')); return
        state=st.selectbox(t('Reference 0+ level'),zero,format_func=lambda i:str(i+1))
        result=invariants(model,state)
        st.json({k:v for k,v in result.items() if k!='contributions'})
        st.download_button(t('Download research results (JSON)'),export_json(dict(inputs=payload,state=state+1,result=result)),'invariants.json','application/json',key='dl_nominal_shape')
        st.bar_chart(pd.DataFrame(result['contributions']).set_index('level') if result['contributions'] else pd.DataFrame())
        st.caption(t('q2 and q3 use the supplied signed E2 network. Missing matrix elements are treated as zero and listed above. beta uses R = 1.2 A^(1/3) fm; gamma is an effective moment ratio. An out-of-range cos(3gamma) is reported without clipping.'))
        covariance=st.file_uploader(t('E2 covariance CSV (all E2 elements in input order)'),type=['csv'],key='shape_cov')
        if covariance:
            parameters=[Parameter('element',i) for i,m in enumerate(model.elements) if m.multipolarity==2]
            cov=pd.read_csv(covariance,header=None).to_numpy()
            payload.update(state=state,covariance=cov.tolist())
            result=job('research_shapes',payload,lambda:dict(inputs=payload,draws=invariant_ensemble(model,parameters,cov,state=state)))
            if result:
                data=pd.DataFrame([{k:r[k] for k in ('q2','q3','cos3gamma','gamma_effective_deg','beta_effective')} for r in result['draws']])
                st.dataframe(data.describe(percentiles=[.025,.5,.975]))
                st.caption(t('Invalid gamma moment ratios remain missing; the table reports their valid sample count.'))
    elif mode == modes[3]:
        st.download_button(t('Download joint-fit JSON template'),fit_template(model),'joint_fit_template.json','application/json')
        st.caption(t('Replace every placeholder observation. One JSON file can contain multiple energies, targets, count or cross-section datasets, covariance matrices, normalization uncertainties and external strength, lifetime or quadrupole constraints.'))
        upload=st.file_uploader(t('Upload joint-fit JSON'),type=['json'])
        if upload:
            try:
                config,parameters,experiments=load_fit(upload.getvalue().decode('utf-8-sig'))
                payload['fit']=config
                st.dataframe(pd.DataFrame([dict(experiment=i+1,kind=e.kind,observations=len(e.data),likelihood=e.likelihood) for i,e in enumerate(experiments)]),hide_index=True)
                def run():
                    fit=joint_fit(model,parameters,experiments,config['bounds'],config.get('starts'),settings,config.get('max_nfev',100))
                    if config.get('profile'):
                        p=config['profile']
                        fit['profile']=profile_fit(model,parameters,experiments,config['bounds'],p['parameter']-1,p['grid'],settings,config.get('max_nfev',100))
                    return dict(inputs=payload,fit=fit)
                result=job('research_fit',payload,run)
                if result:
                    fit=result['fit']; st.json(json.loads(export_json(fit)),expanded=False)
                    if not fit['success']: st.warning(t('The optimizer did not converge. Treat these values as an unfinished fit.'))
                    if fit['covariance'] is None: st.warning(t('Local covariance is unavailable because the solution is singular or touches a bound.'))
                    else:
                        cov=np.asarray(fit['covariance']); sd=np.sqrt(np.diag(cov)); corr=cov/np.outer(sd,sd)
                        st.plotly_chart(go.Figure(go.Heatmap(z=corr,zmin=-1,zmax=1,colorscale='RdBu')))
                    st.caption(t('Covariance is a local linear approximation without chi-square rescaling. Inspect all starting solutions and profile scans for sign ambiguities and non-Gaussian intervals.'))
            except (ValueError,KeyError,TypeError) as error: st.error(error_text(error))
    elif mode == modes[4]:
        st.caption(t('Branches are total decay fractions including conversion. Alpha is an evaluated input. Incomplete networks retain unassigned probability as a sink. Angular response uses pure electric transitions in the emitter rest frame and solver orbit axes; it is not a laboratory Doppler or geometry correction.'))
        rates=decay_rates(model)
        st.dataframe(rates,hide_index=True)
        defaults=[]
        if not rates.empty:
            defaults=[dict(upper=int(r.upper),lower=int(r.lower),branch=r.total_branch,alpha=0.,multipolarity=int(r.lam)) for r in rates.itertuples()]
        network_upload=st.file_uploader(t('Upload decay network CSV'),type=['csv'],key='decay_upload')
        default_frame=pd.read_csv(network_upload) if network_upload else pd.DataFrame(defaults,columns=['upper','lower','branch','alpha','multipolarity'])
        editor_source = json.dumps(asdict(model),sort_keys=True)+default_frame.to_csv(index=False)
        editor_key = 'decay_edges_'+hashlib.sha256(editor_source.encode()).hexdigest()[:12]
        frame=st.data_editor(default_frame,num_rows='dynamic',key=editor_key,hide_index=True)
        angle=st.number_input(t('Collision CM angle (°)'),min_value=.1,max_value=180.,value=90.)
        theta_min=st.number_input(t('Photon detector minimum polar angle (°)'),min_value=0.,max_value=179.,value=30.)
        theta_max=st.number_input(t('Photon detector maximum polar angle (°)'),min_value=1.,max_value=180.,value=60.)
        gate=st.checkbox(t('Condition on a first photon (gamma-gamma correlation)'),value=False)
        gate_edge=st.number_input(t('First photon transition (row number)'),min_value=1,max_value=max(1,len(frame)),value=1)
        gate_theta=st.number_input(t('First photon polar angle (°)'),min_value=0.,max_value=180.,value=0.)
        payload.update(edges=frame.to_dict('records'),angle=angle,photon_acceptance=[theta_min,theta_max],gate=gate,gate_edge=gate_edge,gate_theta=gate_theta)
        def run():
            for column in ('upper','lower','multipolarity'):
                if not np.all(np.isfinite(frame[column])) or not np.all(frame[column]==np.floor(frame[column])):
                    raise ValueError('Decay indices and multipolarity must be finite integers.')
            transitions=tuple(Transition(int(r.upper)-1,int(r.lower)-1,float(r.branch),float(r.alpha),int(r.multipolarity)) for r in frame.itertuples())
            missing=validate_network(model,transitions)
            collision=CoupledChannels(model).solve(angle,settings)
            occupancy,photons=cascade(model,collision.probabilities,transitions)
            result=dict(inputs=payload,occupancy=occupancy,photons=photons,unassigned_branches=missing,rates=rates)
            if not any(e.alpha for e in transitions):
                rho=cascade_densities(model,collision.density_matrices,transitions)
                if gate:
                    edge=transitions[gate_edge-1]
                    conditioned=edge.branch*photon_map(rho[edge.upper],model.levels[edge.upper].spin,
                        model.levels[edge.lower].spin,edge.multipolarity,np.deg2rad(gate_theta),0.)
                    probability=np.trace(conditioned).real
                    if probability<=0: raise ValueError('The selected first-photon direction has zero probability.')
                    initial=[np.zeros_like(x) for x in rho]
                    initial[edge.lower]=conditioned/probability
                    rho=cascade_densities(model,initial,transitions)
                    result['gate_density_per_sr']=probability
                    result['angular_normalization']='conditional on first photon, per subsequent photon per sr'
                theta=np.linspace(0,np.pi,181); angular=[]; acceptance=[]
                for edge in transitions:
                    ji,jf=model.levels[edge.upper].spin,model.levels[edge.lower].spin
                    angular.append([edge.branch*np.trace(photon_map(rho[edge.upper],ji,jf,edge.multipolarity,x,0.)).real for x in theta])
                    acceptance.append(edge.branch*fold_detector(rho[edge.upper],ji,jf,edge.multipolarity,np.deg2rad(theta_min),np.deg2rad(theta_max)))
                result.update(theta_deg=np.degrees(theta),angular=angular,detected_photons=acceptance)
            return result
        result=job('research_decay',payload,run)
        if result:
            st.dataframe(pd.DataFrame({'transition':np.arange(len(result['photons']))+1,'photons_per_collision':result['photons']}),hide_index=True)
            if 'angular' in result:
                if gate:
                    st.info(t('Angular curves and detector acceptance are conditional on the first photon. The yield table remains ungated.'))
                fig=go.Figure()
                for i,y in enumerate(result['angular']): fig.add_scatter(x=result['theta_deg'],y=y,name=str(i+1))
                st.plotly_chart(style(fig,t('Photon polar angle (°), φ = 0'),t('Photons per collision per sr')))
                st.write(t('Photons in the full-azimuth rest-frame annulus'),result['detected_photons'])
            else: st.info(t('Conversion is included in photon yields. Aligned cascade response with conversion requires electron transfer tensors and is not calculated.'))
    else:
        st.caption(t('Compare E3 strengths, diagonal E2 reorientation, polarization and explicit model-space truncations. These are alternative input models; E3 strength alone does not establish permanent octupole deformation.'))
        scenarios=st.data_editor(pd.DataFrame([dict(name='baseline',e3_scale=1.,diagonal_e2_scale=1.,dipole_strength=model.dipole_strength,max_level=len(model.levels)),dict(name='no E3',e3_scale=0.,diagonal_e2_scale=1.,dipole_strength=model.dipole_strength,max_level=len(model.levels)),dict(name='opposite reorientation',e3_scale=1.,diagonal_e2_scale=-1.,dipole_strength=model.dipole_strength,max_level=len(model.levels)),dict(name='no polarization',e3_scale=1.,diagonal_e2_scale=1.,dipole_strength=0.,max_level=len(model.levels))]),num_rows='dynamic',hide_index=True,key='research_scenarios')
        payload['scenarios']=scenarios.to_dict('records')
        def run():
            angles=np.linspace(30,180,11); rows=[]
            for row in scenarios.itertuples():
                n=int(row.max_level)
                if not 1 <= n <= len(model.levels): raise ValueError('Model truncation must retain at least the ground state.')
                elements=tuple(replace(m,value=m.value*(row.e3_scale if m.multipolarity==3 else row.diagonal_e2_scale if m.multipolarity==2 and m.initial==m.final else 1.)) for m in model.elements if max(m.initial,m.final)<n)
                local=replace(model,levels=model.levels[:n],elements=elements,dipole_strength=row.dipole_strength)
                scan=calculate(local,angles,settings,**workflow)
                for i,a in enumerate(angles):
                    for l in range(n): rows.append(dict(scenario=row.name,angle=a,level=l+1,probability=scan.probabilities[i,l],cross_section=scan.cross_sections[i,l]))
            return dict(inputs=payload,rows=rows)
        result=job('research_models',payload,run)
        if result:
            data=pd.DataFrame(result['rows']); fig=go.Figure()
            for (name,level),group in data[data.level>1].groupby(['scenario','level']): fig.add_scatter(x=group.angle,y=group.probability,name=f'{name} · {level}')
            st.plotly_chart(style(fig,t('CM angle (°)'),t('Population probability')))
            st.dataframe(data,hide_index=True)
