"""Result exploration and exports, using completed calculations only."""
from dataclasses import asdict
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from .i18n import t
from .observables import lab_angle, lab_jacobian, surface_separation
from .plots import COLORS, curves, label, style
from .workflow import results_frame


def chart(figure, signature, alt, key):
    figure.update_layout(uirevision=signature)
    st.plotly_chart(figure, alt=alt, key=key, config={'displaylogo': False, 'scrollZoom': False,
                                          'toImageButtonOptions': {'scale': 2}})


def render(result):
    reaction, scan = result['model'], result['scan']
    signature = result['signature']
    st.subheader(t('Explore your results'), anchor=False)
    st.caption(f"{reaction.title} · {reaction.energy_lab:g} MeV · {t(reaction.excitation.capitalize())} · "
               f"{t('{count} angles', count=len(scan.angles))} · {result['seconds']:.1f} s")
    excited = scan.probabilities[:, 1:].sum(axis=1)
    peak = int(np.argmax(excited))
    separation = surface_separation(reaction, scan.angles)
    with st.container(key='result_metrics'):
        a, b, c, d = st.columns(4)
        a.metric(t('Peak total excitation'), f'{excited[peak]:.2%}')
        b.metric(t('At sampled CM angle'), f'{scan.angles[peak]:g}°')
        c.metric(t('Minimum surface separation'), f'{min(separation):.2f} fm')
        d.metric(t('Maximum probability drift'), f'{max(scan.norm_errors):.2e}')
    st.caption(t('Extrema refer to the calculated angle grid. Probability drift measures normalization, not total numerical error.'))
    if np.any(separation < 5):
        st.warning(t('Some angles fall below the 5 fm separation guideline. Inspect Closest approach before interpreting this as a pure Coulomb result.'))
    if len(scan.angles) == 1:
        st.info(t('One angle was calculated. Use the angle inspector for its values, or widen the range for angular curves.'))

    # Reset only when the level scheme changes. Choices persist across language switches.
    scheme = tuple((level.spin, level.energy, level.parity) for level in reaction.levels)
    if st.session_state.get('_plot_scheme') != scheme:
        st.session_state['_plot_scheme'] = scheme
        st.session_state['plot_levels'] = list(range(1, min(5, len(scheme)))) or [0]
    selected = st.multiselect(t('Levels to plot'), list(range(len(reaction.levels))),
                              format_func=lambda i: label(i, reaction.levels[i]), key='plot_levels',
                              help=t('Choose levels here; click a plot legend to hide a curve, or double-click to isolate it.'))
    if not selected:
        st.info(t('Select at least one level to display curves. Complete numerical results remain available for download.'))
    population_tab, cross_tab, approach_tab, data_tab = st.tabs([
        t('Populations'), t('Cross sections'), t('Closest approach'), t('Data and downloads')],
        key='result_tab', on_change='rerun')
    with population_tab:
        st.caption(t('Each curve is the final population of one nuclear level, averaged over initial magnetic substates.'))
        log_p = st.checkbox(t('Logarithmic probability axis'), key='log_probability')
        if log_p:
            st.caption(t('Zero values are omitted on logarithmic axes; exported data retain the original values.'))
        if selected:
            chart(curves(reaction, scan.angles, scan.probabilities, t('CM scattering angle (°)'),
                         t('Level population probability'), selected, log_p), signature,
                  t('Population probability versus angle'), 'population_plot')
        st.markdown(f"**{t('Inspect a calculated angle')}**")
        angle = st.select_slider(t('Calculated CM angle (°)'), options=scan.angles.tolist(),
                                 value=float(scan.angles[np.argmin(abs(scan.angles-90))]), key='inspect_result_angle')
        row = int(np.argmin(abs(scan.angles-angle)))
        inspection = pd.DataFrame({t('Level'): [label(i, level) for i, level in enumerate(reaction.levels)],
                                   t('Population (%)'): 100*scan.probabilities[row],
                                   'dσ/dΩcm (barn/sr)': scan.cross_sections[row]})
        st.dataframe(inspection, hide_index=True, column_config={
            t('Population (%)'): st.column_config.NumberColumn(format='%.6g'),
            'dσ/dΩcm (barn/sr)': st.column_config.NumberColumn(format='%.6g')}, alt=t('Values at the selected calculated angle'))
        st.caption(t('These are calculated grid points, without interpolation.'))
    with cross_tab:
        log_cs = st.checkbox(t('Logarithmic cross-section axis'), value=True, key='log_cs')
        if selected:
            chart(curves(reaction, scan.angles, scan.cross_sections, t('CM scattering angle (°)'),
                         'dσ/dΩcm (barn/sr)', selected, log_cs), signature,
                  t('Differential cross section versus angle'), 'cross_section_plot')
        with st.expander(t('Laboratory-frame curves'), icon=':material/rotate_right:'):
            if len(scan.energies) == 1:
                fig = go.Figure()
                for i in selected:
                    x = lab_angle(reaction, scan.angles, reaction.levels[i].energy)
                    y = scan.cross_sections[:, i]*lab_jacobian(reaction, scan.angles, reaction.levels[i].energy)
                    y = np.where(np.isfinite(y) & ((y > 0) if log_cs else True), y, np.nan)
                    fig.add_scatter(x=x, y=y, name=label(i, reaction.levels[i]), mode='lines+markers',
                                    connectgaps=False, line=dict(color=COLORS[i % len(COLORS)]))
                style(fig, t('Scattered projectile lab angle (°)'), t('dσ/dΩlab per branch (barn/sr)'))
                if log_cs:
                    fig.update_yaxes(type='log')
                if selected:
                    chart(fig, signature, t('Lab-frame cross section'), 'lab_plot')
                st.caption(t('Lab curves include the solid-angle Jacobian and exit-channel speed. For a heavy projectile, two CM '
                             'branches may reach the same lab angle; sum their contributions. Detector integration below '
                             'includes both branches without sampling the singular turning point.'))
            else:
                st.info(t('A thick target has a different lab-angle mapping at each depth. Use Detector yields or Measurements to integrate the depth-dependent acceptance.'))
    with approach_tab:
        fig = go.Figure(go.Scatter(x=scan.angles, y=separation, mode='lines+markers', name=t('Surface separation')))
        fig.add_hline(y=5, line_dash='dash', annotation_text=t('Traditional 5 fm guideline'))
        style(fig, t('CM scattering angle (°)'), t('Surface separation at closest approach (fm)'))
        chart(fig, signature, t('Surface separation versus angle'), 'separation_plot')
        st.caption(t('The nuclear-radius estimate is 1.25 A^(1/3) fm. Below the guideline, nuclear interactions may invalidate '
                     'a pure Coulomb calculation. For energy-loss runs this plot uses the incident energy, the smallest '
                     'separation in the target.'))
        st.info(t('A separation above the guideline is not a validation of the model. Check level-space truncation and convergence in Help and reference → Verification.'))
    with data_tab:
        a, b = st.columns(2)
        a.metric(t('Beam energy sampled'), f'{min(scan.energies):.2f}–{max(scan.energies):.2f} MeV')
        b.metric(t('Depth samples'), len(scan.energies))
        frame = results_frame(reaction, scan)
        st.caption(t('CSV contains every level and angle. JSON also includes the physical inputs, solver settings and target-depth data.'))
        payload = dict(reaction=asdict(reaction), solver=asdict(result['settings']), input_text=result['text'],
                       stopping_csv=result['stopping_text'], thickness_mg_cm2=result['thickness'], depth_order=result['order'],
                       depth_energies_MeV=scan.energies.tolist(), depth_weights=scan.weights.tolist(),
                       depth_cross_sections_barn_sr=scan.depth_cross_sections.tolist(), results=frame.to_dict('records'))
        with st.container(horizontal=True):
            st.download_button(t('Download results CSV'), frame.to_csv(index=False), 'coulex_results.csv', 'text/csv',
                               key='download_results', icon=':material/download:')
            st.download_button(t('Download reproducible calculation JSON'), json.dumps(payload, indent=2), 'coulex_calculation.json',
                               'application/json', key='download_json', icon=':material/download:')
        st.dataframe(frame, hide_index=True, alt=t('Numerical results'))
