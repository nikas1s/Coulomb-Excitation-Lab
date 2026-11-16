"""Reaction setup: a built-in example, the user's reaction file, or the user's own tables.

Examples are only used when "Built-in example" is selected. The two "own data"
modes start empty and never fall back to example numbers.
"""
from dataclasses import dataclass, field
import hashlib
import pandas as pd
import streamlit as st
from .examples import BY_KEY, EXAMPLES, KIND_LABELS
from .help_ui import format_box
from .i18n import error_text, t
from .imports import nuclear_tables, reaction_text, read_table
from .model import parse_input

MODES = ('example', 'file', 'tables')
LEVEL_COLUMNS = ('level', 'spin', 'energy_mev', 'parity', 'k')
ELEMENT_COLUMNS = ('initial', 'final', 'value', 'lambda')
KIND_BADGES = {'literature': ('green', ':material/menu_book:'),
               'teaching': ('violet', ':material/school:')}


@dataclass
class Draft:
    """What the user has specified so far; `base` is None until it is complete."""
    mode: str
    source: tuple                  # identity of the reaction source
    base: object = None            # parsed Reaction (example or file)
    text: str | None = None
    example: object = None
    problems: list = field(default_factory=list)
    nuclei: dict | None = None     # tables mode: title, Z/A, levels, elements


def _digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def _mode_label(mode):
    return {'example': t('Built-in example'), 'file': t('My own reaction file'), 'tables': t('My own tables')}[mode]


def reaction_input(root, table_container):
    # Labels are frozen at creation so the widget never formats in another language.
    labels = {mode: _mode_label(mode) for mode in MODES}
    mode = st.radio(t('Reaction source'), MODES, key='reaction_source', format_func=labels.__getitem__,
                    captions=[t('Ready-made reactions with documented sources'),
                              t('Upload a reaction text file (.txt/.dat)'),
                              t('Type or upload levels and matrix elements')])
    if mode == 'example':
        return _example_input()
    if mode == 'file':
        return _file_input(root)
    return _table_input(root, table_container)


def _parse(mode, source, text, example=None):
    """Parse reaction text; an error is shown here and keeps the same source (results are not discarded)."""
    try:
        return Draft(mode, source, parse_input(text), text, example)
    except ValueError as error:
        st.error(error_text(error), icon=':material/error:')
        return Draft(mode, source, None, text, example,
                     problems=[t('Correct the reaction input: see the error message in the sidebar.')])


def _editable_text(text):
    with st.expander(t('View or edit the input text'), icon=':material/edit:'):
        text = st.text_area(t('Reaction input text'), text, height=330, key='input_'+_digest(text))
        st.caption(t('Beam energy is total MeV. Level and transition indices start at 1. '
                     'Eλ elements use e·b^(λ/2). Text after # is a comment.'))
    return text


def _example_input():
    key = st.selectbox(t('Example'), [example.key for example in EXAMPLES], key='example')
    example = BY_KEY[key]
    color, icon = KIND_BADGES[example.kind]
    st.badge(t(KIND_LABELS[example.kind]), color=color, icon=icon)
    st.caption(t(example.summary))
    draft = _parse('example', ('example', key), _editable_text(example.text()), example)
    if draft.base is not None:
        st.download_button(t('Download reaction text'), reaction_text(draft.base), example.filename,
                           'text/plain', key='download_example', icon=':material/download:', width='stretch')
    return draft


def _file_input(root):
    format_box('tclx', root, 'sidebar')
    upload = st.file_uploader(t('Upload your reaction file'), type=['txt', 'dat'], key='reaction_file')
    if not upload:
        st.info(t('No file yet. Nothing is calculated until you upload your own input.'), icon=':material/upload:')
        return Draft('file', ('file', None), problems=[t('Upload your reaction file (sidebar, step 1).')])
    data = upload.getvalue()
    source = ('file', _digest(data))
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        message = t('The file is not UTF-8 text. Save it as plain text (UTF-8) and upload it again.')
        st.error(message, icon=':material/error:')
        return Draft('file', source, problems=[message])
    return _parse('file', source, _editable_text(text))


def _empty(columns, integer=()):
    return pd.DataFrame({name: pd.Series(dtype='Int64' if name in integer else 'float') for name in columns})


def _table(title, key, columns, integer, root, help_text):
    st.markdown(f'**{title}**')
    format_box(key, root, 'tables')
    upload = st.file_uploader(t('Upload a CSV file (optional)'), type=['csv', 'tsv', 'txt'], key=f'{key}_file')
    frame = read_table(upload.getvalue().decode('utf-8-sig')) if upload else _empty(columns, integer)
    editor_key = f'{key}_editor_'+_digest(frame.to_csv(index=False))
    config = {name: st.column_config.Column(help=help_text[name]) for name in columns if name in frame}
    edited = st.data_editor(frame, num_rows='dynamic', hide_index=True, key=editor_key, column_config=config,
                            alt=title)
    # Rows the user added but left completely empty are ignored.
    return edited.replace('', pd.NA).dropna(how='all')


def _table_input(root, table_container):
    st.caption(t('Enter the nuclei here and the level scheme on the main page.'))
    title = st.text_input(t('Reaction title'), key='table_title', placeholder=t('e.g. my experiment'))
    left, right = st.columns(2)
    zp = left.number_input(t('Projectile Z'), min_value=1, step=1, value=None, key='table_zp')
    ap = right.number_input(t('Projectile A'), min_value=1, step=1, value=None, key='table_ap')
    zt = left.number_input(t('Target Z'), min_value=1, step=1, value=None, key='table_zt')
    at = right.number_input(t('Target A'), min_value=1, step=1, value=None, key='table_at')
    problems = [t('Enter {name} (sidebar, step 1).', name=name) for name, value in
                ((t('Projectile Z'), zp), (t('Projectile A'), ap), (t('Target Z'), zt), (t('Target A'), at))
                if value is None]
    with table_container:
        st.subheader(t('Your level scheme'), anchor=False)
        st.markdown(t('Fill in both tables (add rows with **+**) or upload CSV files. They start empty: '
                      'nothing from the examples is used here. Measured cross sections or counts belong in '
                      'the **Measurements** tab, not in these tables.'))
        left, right = st.columns(2)
        with left:
            levels = _table(t('Nuclear levels'), 'levels', LEVEL_COLUMNS, ('level', 'parity'), root,
                            {'level': t('Level number 1, 2, 3 … in order, without gaps'),
                             'spin': t('Spin J: integer or half-integer (0, 2, 1.5 …)'),
                             'energy_mev': t('Excitation energy; level 1 must be the ground state at 0'),
                             'parity': t('Parity: 1 for +, −1 for −'),
                             'k': t('K quantum number, kept as metadata only (default 0)')})
        with right:
            elements = _table(t('Electric matrix elements'), 'matrix_elements', ELEMENT_COLUMNS,
                              ('initial', 'final', 'lambda'), root,
                              {'initial': t('Level number of the first state'),
                               'final': t('Level number of the second state (equal to initial for a diagonal element)'),
                               'value': t('Signed reduced matrix element <initial‖Eλ‖final> (e·b for E2). '
                                          'Not B(Eλ): for a 0+ ground state, value = ±√B(Eλ↑)'),
                               'lambda': t('Electric multipolarity λ = 1, 2, 3 or 4')})
    source = ('tables',)
    if levels.empty:
        problems.append(t('Add at least the ground state to the level table (level 1, energy 0 MeV).'))
        return Draft('tables', source, problems=problems)
    try:
        states, couplings = nuclear_tables(levels.astype(object), elements.astype(object))
    except ValueError as error:
        with table_container:
            st.error(error_text(error), icon=':material/error:')
        return Draft('tables', source, problems=[*problems, t('Correct the level or matrix-element table (see the error above the tabs).')])
    if problems:
        return Draft('tables', source, problems=problems)
    nuclei = dict(title=title.strip() or t('My reaction'), projectile_z=int(zp), projectile_a=int(ap),
                  target_z=int(zt), target_a=int(at), levels=states, elements=couplings)
    return Draft('tables', source, nuclei=nuclei)
