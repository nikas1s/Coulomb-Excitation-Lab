"""Streamlit frontend; numerical work is confined to the independently testable package."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from coulex import CoupledChannels, Reaction, SolverSettings
from coulex.examples import DATA_SOURCES, KIND_LABELS
from coulex.help_ui import format_box, formats_tab, instructions, quick_start
from coulex.i18n import LANGUAGE_KEY, LANGUAGES, doc, error_text, t
from coulex.i18n_el import EL
from coulex.input_ui import reaction_input
from coulex.literature import REFERENCES
from coulex.measurement_ui import render_measurements
from coulex.model import angle_grid
from coulex.observables import integrate_detector, particle_yield
from coulex.plots import COLORS, collision_plot, curves, label, levels, orbit, style
from coulex.results_ui import render as render_results
from coulex.stopping import StoppingTable
from coulex.verification_ui import render as render_verification
from coulex.workflow import calculate
from coulex.research_ui import render as render_research

ROOT = Path(__file__).resolve().parent
# Results and checks that belong to one reaction source; they are discarded when the source changes.
RESULT_KEYS = ('calculation', 'dynamics', 'accuracy', 'measurement_comparison', 'detector_result')

st.set_page_config(page_title='Coulomb Excitation Lab', page_icon='⚛', layout='wide')
st.html('''<style>
[data-testid="stMainBlockContainer"] {padding-top: 2rem; padding-bottom: 2rem;}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {gap: .75rem;}
[data-testid="stMainBlockContainer"] h1 {font-size: clamp(1.7rem, 3vw, 2.5rem);}
.st-key-result_metrics [data-testid="stMetricLabel"] {height: auto; min-height: 1.5rem;}
.st-key-result_metrics [data-testid="stMetricLabel"] p {white-space: normal; overflow: visible;}
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] {padding-top: 3.5rem; padding-left: 1rem; padding-right: 1rem;}
  .st-key-result_metrics [data-testid="stHorizontalBlock"] {display: grid; grid-template-columns: 1fr 1fr;}
  .st-key-result_metrics [data-testid="stColumn"] {width: 100%; min-width: 0;}
}
</style>''')


def follow(key, source, value):
    """Reset a keyed widget to `value` when its source or source value changes; keep user edits otherwise."""
    marker = f'_follow_{key}'
    if st.session_state.get(marker) != (source, value):
        st.session_state[marker] = (source, value)
        st.session_state[key] = value


def show_error(error):
    st.error(error_text(error), icon=':material/error:')


# Choice widgets whose option labels are translated. Streamlit stores such a choice by its displayed label,
# so a language switch would reset it; the callback re-asserts the internal value before the rerun.
TRANSLATED_CHOICES = ('reaction_source', 'excitation', 'measurement_kind', 'measurement_source',
                      'public_nucleus')
TRANSLATED_PREFIXES = ('measurement_frame_',)  # map_* selectboxes keep their raw values and need no help


NAVIGATION = {
    'section_tab': [(':material/calculate:', 'Calculation'), (':material/help:', 'Help and reference')],
    'work_tab': [(':material/account_tree:', 'Level scheme'), (':material/show_chart:', 'Results'),
                 (':material/timeline:', 'During the collision'), (':material/sensors:', 'Detector yields'),
                 (':material/upload_file:', 'Measurements'), (':material/science:', 'Research')],
    'result_tab': [('', 'Populations'), ('', 'Cross sections'), ('', 'Closest approach'), ('', 'Data and downloads')],
}


def keep_choices_on_language_change():
    for key, options in NAVIGATION.items():
        current = st.session_state.get(key)
        for icon, name in options:
            if current in {f'{icon} {name}'.strip(), f'{icon} {EL.get(name, name)}'.strip()}:
                st.session_state[key] = f'{icon} {t(name)}'.strip()
                break
    for key in list(st.session_state):
        if key in TRANSLATED_CHOICES or str(key).startswith(TRANSLATED_PREFIXES):
            st.session_state[key] = st.session_state[key]


def open_results():
    st.session_state['section_tab'] = f":material/calculate: {t('Calculation')}"
    st.session_state['work_tab'] = f":material/show_chart: {t('Results')}"


with st.sidebar:
    st.segmented_control('Language · Γλώσσα', list(LANGUAGES), format_func=LANGUAGES.__getitem__, key=LANGUAGE_KEY,
                         default='en', required=True, bind='query-params', on_change=keep_choices_on_language_change)

st.title(t('Coulomb Excitation Lab'), anchor=False)
st.caption(t('An interactive laboratory for nuclear physics'))

# The working screen comes first; guide, formats, verification and physics live in a separate help section.
# Both are tabs (not pages) so that widgets in the calculation views keep their state while help is open.
work_tab, help_tab = st.tabs([f":material/calculate: {t('Calculation')}", f":material/help: {t('Help and reference')}"],
                              key='section_tab', on_change='rerun')
with work_tab:
    status = st.container()
    table_container = st.container()
    work_names = [(':material/account_tree:', 'Level scheme'), (':material/show_chart:', 'Results'),
                  (':material/timeline:', 'During the collision'), (':material/sensors:', 'Detector yields'),
                  (':material/upload_file:', 'Measurements'), (':material/science:', 'Research')]
    overview, results_tab, dynamics_tab, yields_tab, measurements_tab, research_tab = st.tabs(
        [f'{icon} {t(name)}' for icon, name in work_names], key='work_tab', on_change='rerun')
with help_tab:
    help_names = [(':material/school:', 'Guide'), (':material/description:', 'File formats'),
                  (':material/verified:', 'Verification'), (':material/menu_book:', 'Physics')]
    guide_tab, formats_tab_, verification_tab, physics_tab = st.tabs([f'{icon} {t(name)}' for icon, name in help_names])

model, draft, problems = None, None, []
with st.sidebar:
    st.header(t('1 · Reaction'), anchor=False)
    try:
        draft = reaction_input(ROOT, table_container)
    except (ValueError, UnicodeDecodeError) as error:
        show_error(error)
    problems = list(draft.problems) if draft else [t('Correct the reaction input (see the error in the sidebar).')]
    base, example = (draft.base, draft.example) if draft else (None, None)
    source = draft.source if draft else ('invalid',)

    st.header(t('2 · Beam and angles'), anchor=False)
    follow('beam_energy', source, float(base.energy_lab) if base else None)
    energy = st.number_input(t('Beam energy (total MeV)'), min_value=.001, value=None, format='%.3f', key='beam_energy',
                             help=t('Kinetic energy of the whole beam nucleus: MeV/u × mass number.'))
    nuclei = base if base else (draft.nuclei if draft and draft.nuclei else None)
    projectile_a = (nuclei.projectile_a if base else nuclei['projectile_a']) if nuclei else None
    if energy and projectile_a:
        st.caption(t('= {value} MeV per nucleon', value=f'{energy/projectile_a:.4g}'))
    if energy is None:
        problems.append(t('Enter the beam energy (sidebar, step 2).'))
    follow('excitation', source, example.excitation if example else 'projectile')
    excitation = st.segmented_control(t('Excited nucleus'), ['projectile', 'target'], key='excitation', required=True,
                                      format_func={'projectile': t('Projectile'), 'target': t('Target')}.__getitem__)
    st.caption(t('The level scheme belongs to the excited nucleus.'))
    if base is not None:
        follow('use_file_angles', source, draft.mode == 'file')
        use_file = st.checkbox(t('Use angle range from input file'), key='use_file_angles')
    else:
        use_file = False
    defaults = ((base.theta_min, base.theta_max, base.theta_step) if use_file and base else
                example.angles if example else (20., 180., 10.))
    for key, value in zip(('theta_min', 'theta_max', 'theta_step'), defaults):
        follow(key, (source, use_file), float(value))
    minimum = st.number_input(t('Minimum CM angle (°)'), min_value=.000001, max_value=180., format='%.2f', key='theta_min')
    maximum = st.number_input(t('Maximum CM angle (°)'), min_value=.000001, max_value=180., format='%.2f', key='theta_max')
    step = st.number_input(t('Angle step (°)'), min_value=.000001, format='%.2f', key='theta_step',
                           help=t('Smaller steps give smoother curves and more accurate detector integrals, but take longer.'))

    st.header(t('3 · Target and energy loss'), anchor=False)
    st.session_state.setdefault('thickness', 2.)
    thickness = st.number_input(t('Target thickness (mg/cm²)'), min_value=0., step=.1, key='thickness',
                                help=t('Used for yields and count comparisons.'))
    with st.expander(t('Energy loss through a thick target (optional)'), icon=':material/layers:'):
        st.caption(t('Without a table, a thin target at the selected beam energy is assumed.'))
        format_box('stopping', ROOT, 'sidebar')
        stopping_file = st.file_uploader(t('Stopping-power CSV'), type=['csv'], key='stopping_file')
        order = st.selectbox(t('Depth quadrature points'), [4, 6, 8, 12], index=1, key='depth_order')

    with st.expander(t('4 · Physics and numerical options'), icon=':material/settings:'):
        follow('dipole', source, example.polarization if example else True)
        polarization = st.checkbox(t('Include electric dipole polarization'), key='dipole')
        dipole_strength = st.number_input(t('Polarization strength d (MeV⁻¹)'), min_value=0., value=.005,
                                          step=.0005, format='%.4f', key='dipole_strength', disabled=not polarization,
                                          help=t('D = d Ecm A/Z² for the excited nucleus. The default 0.005 is a model '
                                                 'choice; see Physics for the literature and limitations.'))
        tolerance = st.selectbox(t('Relative tolerance'), [1e-8, 1e-9, 1e-10, 1e-11], index=1,
                                 format_func=lambda x: f'{x:.0e}', key='rtol')
        extra = st.slider(t('Extra orbit range Δω'), 0., 2., 0., .25, key='extra_omega')
        st.caption(t('The absolute tolerance is rtol/1000. Test the finite orbit range separately in Help and reference → '
                     'Verification.'))

    stopping_text = stopping = None
    settings, angles = SolverSettings(), None
    try:
        if stopping_file:
            stopping_text = stopping_file.getvalue().decode('utf-8-sig')
            stopping = StoppingTable.from_csv(stopping_text)
        angles = angle_grid(minimum, maximum, step)
        settings = SolverSettings(rtol=tolerance, atol=tolerance/1000, extra_omega=extra)
        if not problems and energy is not None:
            if base is not None:
                model = replace(base, energy_lab=float(energy))
            else:
                model = Reaction(**draft.nuclei, energy_lab=float(energy))
            model = replace(model, excitation=excitation, dipole_strength=dipole_strength if polarization else 0.)
    except (ValueError, UnicodeDecodeError) as error:
        show_error(error)
        model = None
        problems.append(t('Correct the error shown above.'))

    run = st.button(t('Run calculation'), type='primary', width='stretch', disabled=model is None, key='run',
                    icon=':material/play_arrow:', on_click=open_results)
    if model is None:
        st.caption(t('Complete the steps above to enable the calculation.'))

# Results never carry over from another reaction source (for example from an example to your own data).
if st.session_state.get('_active_source') != source:
    for key in RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state['_active_source'] = source

signature = None
if model is not None:
    signature = hashlib.sha256(json.dumps(dict(model=asdict(model), angles=angles.tolist(), settings=asdict(settings),
                                               stopping=stopping_text, thickness=thickness, order=order),
                                          sort_keys=True).encode()).hexdigest()
with status.container(border=True):
    heading, action = st.columns([3, 1], vertical_alignment='center')
    with heading:
        st.markdown(f"**{t('Your calculation workspace')}**")
        if model is not None:
            count = len(angles)*(order if stopping else 1)
            st.caption(t('{angles} angles · {levels} levels · {count} collision calculations',
                         angles=len(angles), levels=len(model.levels), count=count))

        else:
            st.caption(t('Complete the reaction inputs to begin. Measurement uploads use the same nuclear model.'))
    run_main = action.button(t('Run calculation'), key='run_main', type='primary', disabled=model is None,
                             width='stretch', icon=':material/play_arrow:', on_click=open_results)
run = run or run_main

if run and model is not None:
    progress = status.progress(0., text=t('Integrating coupled amplitudes…'))
    started = time.perf_counter()
    try:
        scan = calculate(model, angles, settings, stopping, thickness, order, lambda x: progress.progress(x))
        st.session_state['calculation'] = dict(model=model, scan=scan, settings=settings, text=draft.text,
                                               stopping_text=stopping_text, thickness=thickness, order=order,
                                               signature=signature, seconds=time.perf_counter()-started)
        st.session_state.pop('dynamics', None)
        st.session_state.pop('accuracy', None)
        st.session_state.pop('detector_result', None)
        st.toast(t('Calculation finished.'), icon=':material/check_circle:')
    except (ValueError, RuntimeError) as error:
        with status:
            show_error(error)
    finally:
        progress.empty()

if model is None and problems:
    status.warning('\n'.join(f'- {p}' for p in dict.fromkeys(problems)), title=t('Your reaction is not complete yet'),
               icon=':material/checklist:')

result = st.session_state.get('calculation')
if result and result['signature'] != signature:
    status.info(t('Settings have changed. Run the calculation to update the results; the plots below show the last completed run.'),
            icon=':material/update:')

with guide_tab:
    quick_start()
    instructions()
    st.divider()
    st.caption(t('License: GNU General Public License version 3 — free software, without any warranty. A Python adaptation of '
                 '[TCLX](https://github.com/jhenderson88/TCLX) and its GPL-3.0 successor [Cygnus](https://github.com/jhenderson88/Cygnus) '
                 'by J. Henderson; see LICENSE and README.md.'))

with overview:
    if model is None:
        st.info(t('Define a reaction in the sidebar to see its level scheme.'), icon=':material/info:')
    else:
        if example:
            with st.container(border=True):
                st.markdown(f"**{t('About this example')}** · {t(KIND_LABELS[example.kind])}")
                st.markdown(t(example.summary))
                st.caption(t(example.focus))
                st.caption(t('Sources: {sources}. Details are in Help and reference → Verification.',
                             sources=', '.join(example.sources)))
        else:
            st.markdown(f"**{t('Your own reaction')}**: {model.title}")
        a, b, c = st.columns(3)
        a.metric(t('Centre-of-mass energy'), f'{model.energy_cm:.3f} MeV')
        b.metric(t('Nuclear levels'), len(model.levels))
        c.metric(t('Magnetic substates'), sum(int(2*x.spin+1) for x in model.levels))
        st.plotly_chart(levels(model), alt=t('Level scheme with transition connections'))
        st.caption(t('Line segments are levels; connecting lines represent nonzero transition matrix elements. '
                     'Diagonal elements affect reorientation even though they are not drawn as connections.'))
        st.dataframe(pd.DataFrame([{t('level'): i+1, t('spin'): x.spin, t('Excitation energy (MeV)'): x.energy, t('parity'): x.parity,
                                    'K': x.k} for i, x in enumerate(model.levels)]), hide_index=True, alt=t('Level table'))
        st.dataframe(pd.DataFrame([{t('initial'): x.initial+1, t('final'): x.final+1, 'Eλ': x.multipolarity,
                                    t('matrix element [e·b^(λ/2)]'): x.value} for x in model.elements]),
                     hide_index=True, alt=t('Matrix-element table'))
        if draft.text:
            st.download_button(t('Download the input text'), draft.text, 'coulex_input.txt', 'text/plain',
                               key='download_input', icon=':material/download:')
            st.caption(t('The text download preserves the text editor. The results JSON additionally records all sidebar settings.'))

if result:
    computed, scan, active_settings = result['model'], result['scan'], result['settings']
    with results_tab:
        render_results(result)
    with dynamics_tab:
        detail_angle = st.slider(t('Inspect a CM angle (°)'), 1., 180., 90., 1., key='detail_angle')
        st.caption(t('This view follows one collision at the selected incident energy. A depth-averaged yield is a separate calculation.'))
        left, right = st.columns(2)
        left.plotly_chart(orbit(computed, detail_angle), alt=t('Rutherford trajectory'))
        right.plotly_chart(collision_plot(computed, detail_angle), alt=t('Electric collision functions'))
        if st.button(t('Follow the amplitudes'), key='follow', icon=':material/play_circle:'):
            with st.spinner(t('Resolving the collision history…')):
                try:
                    st.session_state['dynamics'] = (detail_angle, CoupledChannels(computed).solve(detail_angle, active_settings, 401))
                except (ValueError, RuntimeError) as error:
                    show_error(error)
        detail = st.session_state.get('dynamics')
        if detail and detail[0] == detail_angle:
            r = detail[1]
            st.plotly_chart(curves(computed, r.omega, r.history.T, t('Orbit parameter ω (0 = closest approach)'),
                                   t('Instantaneous level population')), alt=t('Population during the collision'))
            st.caption(t('Transient populations need not grow monotonically: the coupled amplitudes interfere and can return '
                         'population to lower levels.'))
            sub = CoupledChannels(computed)
            level = st.selectbox(t('Inspect magnetic substates'), range(len(computed.levels)), index=min(1, len(computed.levels)-1),
                                 format_func=lambda i: label(i, computed.levels[i]), key='substate_level')
            mask = sub.level_index == level
            fig = go.Figure(go.Bar(x=sub.m[mask], y=r.substate_probabilities[mask], marker_color=COLORS[level % len(COLORS)]))
            st.plotly_chart(style(fig, t('Magnetic quantum number m (ℏ)'), t('Final substate probability')),
                            alt=t('Final magnetic-substate populations'))
    with yields_tab:
        st.markdown(t('Integrate the populated cross section over a **scattered-projectile detector annulus**. '
                      'The integral uses CM solid angle and the actual lab acceptance at every target depth.'))
        a, b, c = st.columns(3)
        det_min = a.number_input(t('Detector lab minimum (°)'), min_value=0., max_value=179.99, value=25., key='det_min')
        det_max = b.number_input(t('Detector lab maximum (°)'), min_value=.01, max_value=180., value=55., key='det_max')
        azimuth = c.number_input(t('Azimuth coverage fraction'), min_value=0., max_value=1., value=1., key='azimuth')
        a, b, c = st.columns(3)
        intensity = a.number_input(t('Beam particles per second'), min_value=0., value=1e5, key='intensity')
        days = b.number_input(t('Experiment duration (days)'), min_value=0., value=5., key='days')
        efficiency = c.number_input(t('Particle detection efficiency'), min_value=0., max_value=1., value=1., key='efficiency')
        st.caption(t('Target areal density: {thickness} mg/cm² (from the completed run).', thickness=f"{result['thickness']:g}"))
        gamma = st.checkbox(t('Estimate a direct gamma coincidence for a selected level'), disabled=len(computed.levels) < 2,
                            key='gamma')
        if gamma:
            a, b, c = st.columns(3)
            gamma_level = a.selectbox(t('Gamma-emitting level'), range(1, len(computed.levels)),
                                      format_func=lambda i: label(i, computed.levels[i]), key='gamma_level')
            branching = b.number_input(t('Direct gamma branching fraction'), min_value=0., max_value=1., value=1., key='branching')
            gamma_eff = c.number_input(t('Absolute gamma efficiency'), min_value=0., max_value=1., value=.1, key='gamma_eff')
            st.caption(t('Direct branch only; feeding cascades, internal conversion, and gamma angular correlations are not '
                         'inferred from excitation matrix elements.'))
        detector_signature = (result['signature'], det_min, det_max, azimuth, intensity, days, efficiency,
                              gamma, gamma_level if gamma else None, branching if gamma else None,
                              gamma_eff if gamma else None)
        if st.button(t('Integrate detector yields'), key='integrate', icon=':material/functions:'):
            try:
                records = []
                for level in range(len(computed.levels)):
                    cs = 0.
                    for d, (depth_energy, weight) in enumerate(zip(scan.energies, scan.weights)):
                        local = computed.at_energy(depth_energy)
                        cs += weight*integrate_detector(local, scan.angles, scan.depth_cross_sections[d, :, level],
                                                        det_min, det_max, computed.levels[level].energy, azimuth)
                    count = particle_yield(cs, computed, result['thickness'], intensity, days)*efficiency
                    record = {'level': level+1, 'cross section (barn)': cs, 'detected particles': count}
                    if gamma:
                        record['direct gamma coincidences'] = count*branching*gamma_eff if level == gamma_level else np.nan
                    records.append(record)
                st.session_state['detector_result'] = (detector_signature, pd.DataFrame(records))
            except ValueError as error:
                show_error(error)
        detector_result = st.session_state.get('detector_result')
        if detector_result and detector_result[0] == detector_signature:
            detector_frame = detector_result[1]
            st.dataframe(detector_frame, hide_index=True, alt=t('Detector yields'))
            st.download_button(t('Download detector yields CSV'), detector_frame.to_csv(index=False),
                               'detector_yields.csv', 'text/csv', key='download_detector')
            st.caption(t('Check angular convergence by halving the CM angle step and recalculating. '
                         'A tight ODE tolerance alone does not control detector-integration error.'))
        elif detector_result:
            st.info(t('Detector settings changed. Integrate again to update the counts.'))

else:
    for tab in (results_tab, dynamics_tab, yields_tab):
        with tab:
            st.info(t('Press “Run calculation” in the sidebar to fill this view. Results are only shown for the reaction '
                      'that produced them.'), icon=':material/info:')

with measurements_tab:
    render_measurements(ROOT, model, settings if model else None, stopping, stopping_text, thickness, order)

with verification_tab:
    render_verification(ROOT, draft, result) if draft else st.info(t('Correct the reaction input first.'))

with formats_tab_:
    formats_tab(ROOT)

with physics_tab:
    st.markdown(doc('physics_steps'))
    st.latex(r'\frac{d a_f}{d\omega}=-i\sum_i\sum_{\lambda}\zeta^{(\lambda)}_{fi}Q_{\lambda,|m_i-m_f|}(\epsilon,\omega)'
             r'e^{i(\eta_f-\eta_i)(\epsilon\sinh\omega+\omega)}a_i')
    st.latex(r'\frac{d\sigma_n}{d\Omega}=P_n\frac{d\sigma_{\mathrm{Ruth},n}}{d\Omega},\qquad N_n=\sigma_n N_{\mathrm{target}}\,I\,t')
    st.markdown(doc('physics_scope'))
    st.subheader(t('References'), anchor=False)
    st.markdown('\n'.join(f'- **{key}** — {text}' for key, text in {**REFERENCES, **DATA_SOURCES}.items()))

with research_tab:
    try:
        render_research(model, settings, stopping, thickness, order)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        show_error(error)
