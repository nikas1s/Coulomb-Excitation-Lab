"""Verification tab: literature benchmarks, example provenance, numerical checks, C++ comparison."""
from dataclasses import replace
import numpy as np
import pandas as pd
import streamlit as st
from .examples import BY_KEY, SOURCES
from .i18n import doc, error_text, t
from .literature import AW60_TABLE5, benchmark_suite
from .solver import CoupledChannels


def _fmt(value):
    return f'{value:.6g}'


def _decimals(value):
    text = np.format_float_positional(abs(value), trim='-')
    return len(text.split('.')[1]) if '.' in text else 0


def _with_uncertainty(datum):
    """Literature value with exactly the decimals of the cited value and uncertainty, e.g. '0.611 ± 0.009'."""
    decimals = max(_decimals(datum.literature), _decimals(datum.minus), _decimals(datum.plus))
    value = f'{datum.literature:.{decimals}f}'
    if datum.plus == datum.minus:
        return f'{value} ± {datum.plus:.{decimals}f} {datum.unit}'.strip()
    return f'{value} +{datum.plus:.{decimals}f} −{datum.minus:.{decimals}f} {datum.unit}'.strip()


def literature_benchmarks():
    st.header(t('Benchmarks against published theory'), anchor=False)
    st.markdown(doc('benchmarks_intro'))
    if st.button(t('Run literature benchmarks'), key='run_literature', icon=':material/fact_check:'):
        # Fixed reference kinematics (22Mg + 104Pd, 66 MeV) make the check reproducible; only the
        # nuclei and beam energy are used.
        reference = BY_KEY['22Mg + 104Pd'].reaction()
        progress = st.progress(0., text=t('Comparing the solver with published results…'))
        try:
            st.session_state['literature'] = benchmark_suite(reference, progress=lambda x: progress.progress(x))
        except (ValueError, RuntimeError) as error:
            st.error(error_text(error))
        finally:
            progress.empty()
    rows = st.session_state.get('literature')
    if rows:
        passed = sum(row.passed for row in rows)
        if passed == len(rows):
            st.success(t('All {count} literature benchmarks passed.', count=len(rows)), icon=':material/verified:')
        else:
            st.error(t('{failed} of {count} literature benchmarks failed.', failed=len(rows)-passed, count=len(rows)))
        st.dataframe(pd.DataFrame([{
            t('Benchmark'): t(row.group), t('Check'): t(row.check, **row.params), t('Reference'): row.references,
            t('Published / analytic'): _fmt(row.expected), t('This code'): _fmt(row.computed),
            t('Difference'): f"{row.difference:.1e} {t('relative') if row.relative else t('absolute')}",
            t('Tolerance'): f'{row.tolerance:.0e}', t('Result'): t('pass') if row.passed else t('FAIL')}
            for row in rows]), hide_index=True, alt=t('Literature benchmark results'))
    else:
        st.caption(t('Takes about 5 seconds. Independent of the reaction selected in the sidebar.'))
    with st.expander(t('What each benchmark tests'), icon=':material/info:'):
        st.markdown(doc('benchmarks_detail'))


def example_provenance(draft, result):
    st.header(t('Literature data behind the selected input'), anchor=False)
    example = draft.example
    if example is None:
        st.info(t('You are using your own reaction. Compare your inputs with evaluated data, for example the '
                  'NNDC/ENSDF level data and the B(E2) evaluation of Pritychenko et al. (2016).'), icon=':material/info:')
        return
    reaction = draft.base
    if reaction is None:
        st.info(t('Correct the reaction input first.'))
        return
    rows = []
    for datum in example.data:
        try:
            implied, deviation = datum.implied(reaction), datum.deviation(reaction)
        except (IndexError, ValueError):
            implied, deviation = float('nan'), float('nan')
        consistent = abs(deviation) <= 2
        status = (t('consistent') if consistent else t('differs from literature')) if np.isfinite(deviation) else '—'
        if datum.model and consistent:
            status = t('model prediction agrees with experiment')
        rows.append({t('Quantity'): t(datum.quantity), t('Literature'): _with_uncertainty(datum),
                     t('This input'): f'{implied:.6g} {datum.unit}'.strip(), t('Deviation (σ)'): f'{deviation:+.2f}',
                     t('Status'): status, t('Source'): datum.source})
    st.dataframe(pd.DataFrame(rows), hide_index=True, alt=t('Example input compared with literature values'))
    if example.kind == 'teaching':
        _teaching_comparison(result)
    st.markdown('\n'.join(f'- **{key}** — {SOURCES[key]}' for key in sorted({d.source for d in example.data} | set(example.sources))))


def _teaching_comparison(result):
    table = AW60_TABLE5[2.0]
    if not result or not np.any(np.isclose(result['scan'].angles, 180.)):
        st.info(t('Run the calculation with 180° in the angle grid to compare with AW60 Table 5.'))
        return
    row = int(np.flatnonzero(np.isclose(result['scan'].angles, 180.))[0])
    computed = result['scan'].probabilities[row]
    spins = [level.spin for level in result['model'].levels]
    st.dataframe(pd.DataFrame([{t('Spin I'): f'{spin:g}+', t('AW60 Table 5'): f'{table[int(spin)]:.4f}',
                                t('This calculation'): f'{computed[i]:.4f}',
                                t('Difference'): f'{computed[i]-table[int(spin)]:+.1e}'}
                               for i, spin in enumerate(spins) if int(spin) in table]),
                 hide_index=True, alt=t('Teaching model compared with Alder and Winther Table 5'))


def numerical_checks(result):
    st.header(t('Numerical convergence checks'), anchor=False)
    st.markdown(t('Probability conservation is necessary, but it is not an error estimate. '
                  'Check the ODE error, the omitted distant part of the orbit, and angular sampling separately.'))
    if not result:
        st.info(t('Run a calculation first; these checks use its reaction and solver settings.'))
        return
    computed, active = result['model'], result['settings']
    test_angle = st.select_slider(t('Convergence-check angle (°)'), options=[15, 30, 60, 90, 120, 150, 180], value=90,
                                  key='check_angle')
    if st.button(t('Run independent convergence checks'), key='run_checks', icon=':material/rule:'):
        with st.spinner(t('Comparing tolerances, orbit range, and a second integrator…')):
            try:
                solver = CoupledChannels(computed)
                base = solver.solve(test_angle, active)
                tighter = dict(rtol=max(1e-13, active.rtol/10), atol=max(1e-15, active.atol/10))
                tests = {'Tighter ODE tolerance': replace(active, **tighter, max_step=.04),
                         'Orbit extended by Δω=1': replace(active, extra_omega=active.extra_omega+1),
                         'Independent RK45 integrator': replace(active, method='RK45', **tighter)}
                records = []
                for name, settings in tests.items():
                    check = solver.solve(test_angle, settings)
                    records.append({t('Check'): t(name), t('Max absolute ΔP'): max(abs(check.probabilities-base.probabilities)),
                                    t('Max norm drift'): check.norm_error, t('RHS evaluations'): check.evaluations})
                st.session_state['accuracy'] = (test_angle, pd.DataFrame(records))
            except (ValueError, RuntimeError) as error:
                st.error(error_text(error))
    accuracy = st.session_state.get('accuracy')
    if accuracy and accuracy[0] == test_angle:
        st.dataframe(accuracy[1], hide_index=True, alt=t('Convergence check results'))
        st.caption(t('These are incident-energy checks at one angle. Check additional angles and depth quadrature for '
                     'precision work. Absolute agreement does not guarantee relative accuracy for tiny populations.'))


def original_code(root):
    st.header(t('Comparison with the original C++ code'), anchor=False)
    report = root/'validation/results/REPORT.md'
    if not report.exists():
        st.info(t('The archived comparison report is missing. Restore validation/results from the application distribution.'))
        return
    st.markdown(doc('original_summary'))
    with st.expander(t('Full report (English)'), icon=':material/article:'):
        st.markdown(report.read_text().split('![Original comparison]')[0])
    st.image(str(root/'validation/results/original_comparison.png'),
             alt=t('Original C++ and Python populations versus angle, with residuals'))
    st.download_button(t('Download all original comparisons'), (root/'validation/results/comparison.csv').read_bytes(),
                       'original_comparison.csv', 'text/csv', key='download_original', icon=':material/download:')


def render(root, draft, result):
    st.markdown(doc('verification_intro'))
    literature_benchmarks()
    example_provenance(draft, result)
    numerical_checks(result)
    original_code(root)
