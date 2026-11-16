"""In-app instructions and file-format help, rendered from coulex.formats."""
from pathlib import Path
import pandas as pd
import streamlit as st
from .formats import CSV_RULES, FORMATS, MEASUREMENT_FORMATS, TCLX_LINES, TCLX_TEMPLATE
from .i18n import doc, t


def quick_start():
    """Four-step orientation strip shown above the tabs."""
    steps = (
        (':material/science:', t('Choose a reaction'),
         t('Sidebar step 1: a built-in example, your own reaction file, or your own tables.')),
        (':material/tune:', t('Set the beam and angles'),
         t('Sidebar step 2: beam energy in total MeV, the excited nucleus and the CM angle grid.')),
        (':material/play_arrow:', t('Run the calculation'),
         t('Press “Run calculation” at the bottom of the sidebar.')),
        (':material/insights:', t('Explore and verify'),
         t('Results appear in the Calculation tabs. Help and reference → Verification checks them against published theory.')),
    )
    columns = st.columns(4)
    for number, (column, (icon, title, body)) in enumerate(zip(columns, steps), 1):
        with column.container(border=True, height='stretch'):
            st.markdown(f'{icon} **{number} · {title}**')
            st.caption(body)


def _columns_frame(fmt):
    return pd.DataFrame([{t('Column'): c.name, t('Required'): t('required') if c.required else t('optional'),
                          t('Unit'): t(c.unit) if c.unit in ('—', 'same as value', 'counts') else c.unit,
                          t('Meaning'): t(c.meaning)} for c in fmt.columns])


def _tclx_frame():
    return pd.DataFrame([{t('Line'): t(line) if line == 'rest' else line, t('Content'): content,
                          t('Meaning'): t(meaning), t('Example'): example}
                         for line, content, meaning, example in TCLX_LINES])


def format_body(key, root: Path, context):
    """Columns, rules, an example preview and template downloads for one file type."""
    fmt = FORMATS[key]
    st.markdown(f"**{t(fmt.purpose)}**")
    st.caption(t('Accepted files: {extensions}. Where: {where}.', extensions=', '.join(fmt.extensions),
                 where=t(fmt.where)))
    if key == 'tclx':
        st.table(_tclx_frame(), hide_index=True, alt=t('Line-by-line layout of a reaction input file'))
    else:
        st.table(_columns_frame(fmt), hide_index=True, alt=t('Required and optional columns'))
    rules = list(fmt.notes) if key in ('tclx', 'stopping') else [*CSV_RULES, *fmt.notes]
    st.markdown('\n'.join(f'- {t(rule)}' for rule in rules))
    example = (root/fmt.example).read_text()
    st.caption(t('{label} — for orientation only; it is never used in your own calculation:', label=t(fmt.example_label)))
    st.code('\n'.join(example.splitlines()[:8])+('\n…' if len(example.splitlines()) > 8 else ''),
            language='text' if key == 'tclx' else 'csv')
    with st.container(horizontal=True):
        if key == 'tclx':
            st.download_button(t('Annotated blank template'), TCLX_TEMPLATE, 'reaction_template.txt', 'text/plain',
                               key=f'blank_{key}_{context}', icon=':material/download:')
        else:
            st.download_button(t('Blank template (headers only)'), fmt.blank_template(), f'{key}_template.csv',
                               'text/csv', key=f'blank_{key}_{context}', icon=':material/download:')
        st.download_button(t(fmt.example_label), example, Path(fmt.example).name,
                           'text/plain' if key == 'tclx' else 'text/csv', key=f'example_{key}_{context}',
                           icon=':material/download:')


def format_box(key, root: Path, context, expanded=False):
    """Compact, expandable version of :func:`format_body` placed beside an uploader."""
    with st.expander(t('Required file format: {title}', title=t(FORMATS[key].title)),
                     icon=':material/description:', expanded=expanded):
        format_body(key, root, context)


def formats_tab(root: Path):
    st.markdown(doc('formats_intro'))
    st.markdown('\n'.join(f'- {t(rule)}' for rule in CSV_RULES))
    sections = (('tclx', 'levels', 'matrix_elements'), ('stopping',), MEASUREMENT_FORMATS)
    titles = (t('Reaction inputs'), t('Target energy loss'), t('Measurements for comparison'))
    for title, keys in zip(titles, sections):
        st.header(title)
        for key in keys:
            st.subheader(t(FORMATS[key].title))
            format_body(key, root, 'tab')


def instructions():
    st.markdown(doc('instructions_intro'))
    with st.container(border=True):
        st.markdown(doc('instructions_example'))
    with st.container(border=True):
        st.markdown(doc('instructions_own'))
    st.subheader(t('Which file goes where'))
    st.table(pd.DataFrame([{t('File'): t(FORMATS[k].title), t('Purpose'): t(FORMATS[k].purpose),
                                t('Where to upload'): t(FORMATS[k].where),
                                t('Required columns'): ', '.join(c.name for c in FORMATS[k].columns if c.required)
                                or t('line-based text, see File formats')}
                               for k in FORMATS]), hide_index=True, alt=t('Upload overview'))  # st.table wraps long text
    st.caption(t('Every format, with blank templates and example files, is under Help and reference → File formats.'))
    st.markdown(doc('instructions_tabs'))
    st.markdown(doc('instructions_units'))
    with st.expander(t('Troubleshooting'), icon=':material/help:'):
        st.markdown(doc('instructions_faq'))
