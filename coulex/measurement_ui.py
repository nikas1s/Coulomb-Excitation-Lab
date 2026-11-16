"""Measurement import, column mapping, comparisons and portable downloads."""
from dataclasses import asdict
import hashlib
import json
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from .formats import FORMATS
from .help_ui import format_box
from .i18n import error_text, t
from .imports import read_table
from .measurements import SCHEMAS, Exposure, validate_measurements, compare_measurements
from .plots import COLORS, style

KINDS = ('cross_section', 'probability', 'particle_counts', 'gamma_counts')
KIND_LABELS = {'cross_section': 'Differential cross sections', 'probability': 'Population probabilities',
               'particle_counts': 'Detected particle counts', 'gamma_counts': 'Direct gamma coincidence counts'}
ALIASES = {'angle_deg': ['theta_cm_deg', 'theta_lab_deg', 'angle', 'theta'],
           'level': ['state', 'level_index'], 'value': ['dsigma_cm_barn_per_sr', 'cross_section', 'counts', 'probability'],
           'uncertainty': ['sigma', 'error', 'uncertainty_barn_sr']}


def render_measurements(root, reaction, settings, stopping, stopping_text, thickness, order):
    st.subheader(t('Compare your measurements with the model'), anchor=False)
    st.markdown(t('Use **one experimental run per table**: the same reaction, beam energy and target conditions. '
                  'The comparison uses the reaction and settings currently selected in the sidebar. '
                  'Nothing is fitted: the matrix elements stay as entered.'))
    if reaction is None:
        st.info(t('Define a complete reaction in the sidebar first; measurements are compared with that model.'),
                icon=':material/info:')
        return
    st.caption(t('Current model: {title}', title=reaction.title))
    # Option labels are frozen at creation (a choice is stored by its displayed label).
    kind = st.selectbox(t('Measured observable'), KINDS, format_func={k: t(KIND_LABELS[k]) for k in KINDS}.__getitem__,
                        key='measurement_kind')
    counts = kind.endswith('counts')
    a, b = st.columns(2)
    frame = a.selectbox(t('Measurement angle frame'), ['Lab', 'CM'] if counts else ['CM', 'Lab'],
                        format_func={'CM': t('CM (centre of mass)'), 'Lab': t('Lab (scattered projectile)')}.__getitem__,
                        disabled=kind == 'probability', key='measurement_frame_'+kind)
    units = b.selectbox(t('Cross-section units'), ['barn/sr', 'mb/sr', 'fm²/sr'],
                        key='measurement_units') if kind == 'cross_section' else None
    if counts:
        st.caption(t('Each row is a detector angular bin. Lab angles always refer to the scattered projectile. '
                     'efficiency is the particle detection fraction for that row, between 0 and 1.'))
    else:
        st.caption(t('Each row is a point measurement at angle_deg. Uncertainty is optional, positive and one-sigma, '
                     'in the same units as value. For finite-bin data, use a corrected point cross section or '
                     'compare detector counts.'))
    format_box(kind, root, 'measurements', expanded=True)
    st.session_state.setdefault('measurement_source', 'upload')
    source = st.segmented_control(t('Import measurements'), ['upload', 'paste'], required=True,
                                  format_func={'upload': t('Upload a file'), 'paste': t('Paste a table')}.__getitem__,
                                  key='measurement_source')
    if source == 'upload':
        upload = st.file_uploader(t('Upload measurements (CSV or TSV)'), type=['csv', 'tsv', 'txt'], key='measurement_file')
        if not upload:
            st.info(t('Upload your file. Required columns: {columns}. Other column names can be matched after upload.',
                      columns=', '.join(SCHEMAS[kind])), icon=':material/upload:')
            return
        try:
            text = upload.getvalue().decode('utf-8-sig')
        except UnicodeDecodeError:
            st.error(t('Export the spreadsheet as CSV UTF-8 or paste its cells below.'))
            return
    else:
        text = st.text_area(t('Paste measurements, including the header row'), height=170, key='measurement_paste',
                            placeholder=FORMATS[kind].blank_template())
        if not text.strip():
            st.info(t('Paste spreadsheet cells including the header row. First line: {header}',
                      header=FORMATS[kind].blank_template().strip()), icon=':material/content_paste:')
            return
    try:
        raw = read_table(text)
        st.caption(t('Preview of your table (first 20 rows)'))
        st.dataframe(raw.head(20), hide_index=True, alt=t('Preview of the imported measurement table'))
        mapping = {}
        with st.expander(t('Match your column names'), expanded=not set(SCHEMAS[kind]).issubset(raw.columns),
                         icon=':material/swap_horiz:'):
            st.caption(t('Select which column of your table holds each quantity. Extra columns are ignored.'))
            for field in (*SCHEMAS[kind], 'uncertainty'):
                choices = ['(not supplied)', *raw.columns]
                suggested = next((x for x in [field, *ALIASES.get(field, [])] if x in raw.columns), '(not supplied)')
                choice = st.selectbox(field, choices, index=choices.index(suggested),
                                      format_func=lambda c, none=t('(not supplied)'): none if c == '(not supplied)' else c,
                                      key=f'map_{kind}_{field}_{hashlib.sha256(text.encode()).hexdigest()}')
                if choice != '(not supplied)':
                    mapping[field] = choice
        if len(set(mapping.values())) != len(mapping):
            raise ValueError('Each selected source column can be mapped to only one quantity.')
        canonical = raw[[mapping[x] for x in mapping]].copy()
        canonical.columns = list(mapping)
        data = validate_measurements(canonical, kind, len(reaction.levels), units or 'barn/sr')
        exposure = Exposure(thickness=thickness)
        angular_step = 1.
        if counts:
            st.markdown(f"**{t('Exposure and acceptance for these counts')}**")
            a, b, c = st.columns(3)
            beam = a.number_input(t('Measurement beam rate (particles/s)'), min_value=.001, value=1e5, key='m_beam')
            days = b.number_input(t('Measurement live duration (days)'), min_value=.000001, value=5., format='%.6f',
                                  key='m_days')
            azimuth = c.number_input(t('Measurement azimuth fraction'), min_value=.000001, max_value=1., value=1.,
                                     key='m_azimuth')
            angular_step = st.selectbox(t('Detector integration CM step (°)'), [2., 1., .5, .25], index=1, key='m_step')
            exposure = Exposure(beam, days, thickness, azimuth)
            if thickness <= 0:
                raise ValueError('Detector-count comparison requires a positive target thickness.')
            st.caption(t('Target thickness: {thickness} mg/cm², from the sidebar. Live duration should account for '
                         'acquisition dead time. Use separate comparisons if the exposure or azimuth coverage changes '
                         'between detectors.', thickness=f'{thickness:g}'))
            if kind == 'gamma_counts':
                st.info(t('Direct gamma coincidences multiply populated-level counts by branching_fraction and '
                          'gamma_efficiency. Both are absolute fractions supplied per row. Feeding, conversion and '
                          'angular correlations are not inferred.'))
        st.success(t('{count} observations validated; levels {levels}.', count=len(data),
                     levels=', '.join(map(str, sorted(set(data.level))))))
    except ValueError as error:
        st.error(error_text(error))
        return
    config = dict(reaction=asdict(reaction), solver=asdict(settings), observable=kind, angle_frame=frame,
                  input_units=units, comparison_units='barn/sr' if kind == 'cross_section' else 'counts' if counts else 'probability',
                  stopping_csv=stopping_text, exposure=asdict(exposure), depth_order=order, angular_step_deg=angular_step,
                  measurements=data.where(data.notna(), None).to_dict('records'))
    signature = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    if st.button(t('Compare measurements'), type='primary', key='compare', icon=':material/compare_arrows:'):
        progress = st.progress(0., text=t('Calculating predictions for the measured angles and acceptance…'))
        try:
            compared = compare_measurements(reaction, data, kind, frame, settings, stopping, exposure, order, angular_step,
                                            lambda x: progress.progress(x))
            st.session_state['measurement_comparison'] = (signature, compared)
        except (ValueError, RuntimeError) as error:
            st.error(error_text(error))
        finally:
            progress.empty()
    stored = st.session_state.get('measurement_comparison')
    if not stored:
        return
    if stored[0] != signature:
        st.info(t('Measurement or reaction settings changed. Compare again to update these predictions.'))
        return
    compared = stored[1]
    ylabel = t(config['comparison_units']) if not kind == 'cross_section' else 'barn/sr'
    fig, residual = go.Figure(), go.Figure()
    for level, group in compared.groupby('level', sort=True):
        color = COLORS[(level-1) % len(COLORS)]
        x = (group.angle_min_deg+group.angle_max_deg)/2 if counts else group.angle_deg
        dx = (group.angle_max_deg-group.angle_min_deg)/2 if counts else np.zeros(len(group))
        errors = group.uncertainty.fillna(0)
        fig.add_scatter(x=x, y=group.value, mode='markers', name=t('Level {level}: measured', level=level),
                        marker=dict(color=color, size=9), error_y=dict(type='data', array=errors),
                        error_x=dict(type='data', array=dx))
        fig.add_scatter(x=x, y=group.predicted, mode='markers', name=t('Level {level}: calculated', level=level),
                        marker=dict(color=color, symbol='x', size=10))
        residual.add_scatter(x=x, y=group.residual, mode='markers', name=t('Level {level}', level=level),
                             marker=dict(color=color, size=8), error_y=dict(type='data', array=errors))
    angle = t('CM') if frame == 'CM' else t('Lab')
    xlabel = t('{frame} detector-bin centre (°)', frame=angle) if counts else t('{frame} scattering angle (°)', frame=angle)
    st.plotly_chart(style(fig, xlabel, ylabel, t('Measurements and predictions')),
                    alt=t('Measured values with error bars and calculated predictions'))
    residual.add_hline(y=0, line_dash='dash')
    st.plotly_chart(style(residual, xlabel, t('Measured − calculated ({unit})', unit=ylabel), t('Residuals')),
                    alt=t('Residuals: measured minus calculated'))
    known = compared.uncertainty.notna()
    if known.any():
        chi2 = float(np.sum(compared.loc[known, 'standardized_residual']**2))
        st.metric('Σ [(measured − calculated) / uncertainty]²', f'{chi2:.4g}')
        st.caption(t('Uses {used} of {total} observations with uncertainties. Assumes independent Gaussian errors; '
                     'no parameters were fitted. Correlated normalization/systematic errors and low-count Poisson '
                     'statistics require a dedicated likelihood analysis.', used=int(known.sum()), total=len(compared)))
    else:
        st.caption(t('No uncertainties supplied: error bars and standardized residuals are unavailable.'))
    st.dataframe(compared, hide_index=True, alt=t('Measurement comparison table'))
    st.download_button(t('Download measurement comparison CSV'), compared.to_csv(index=False), 'measurement_comparison.csv',
                       'text/csv', key='download_comparison_csv', icon=':material/download:')
    config['comparison'] = json.loads(compared.to_json(orient='records', double_precision=15))
    # pandas replaces missing uncertainty values with JSON null, never NaN.
    config['measurements'] = json.loads(data.to_json(orient='records', double_precision=15))
    st.download_button(t('Download measurement comparison JSON'), json.dumps(config, indent=2, allow_nan=False),
                       'measurement_comparison.json', 'application/json', key='download_comparison_json',
                       icon=':material/download:')
    if counts:
        st.info(t('Check detector-integration convergence: halve the CM step and compare again. '
                  'For energy loss, also increase the depth quadrature order.'))
