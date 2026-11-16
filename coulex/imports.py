"""Spreadsheet imports with explicit schemas and no silent unit conversion."""
import csv
from io import StringIO
import numpy as np
import pandas as pd
from .model import Level, MatrixElement


def read_table(text):
    """Read UTF-8 CSV, semicolon CSV or TSV; reject ragged rows and duplicate headers."""
    text = text.lstrip('\ufeff').strip()
    if not text:
        raise ValueError('The uploaded table is empty.')
    header = text.splitlines()[0]
    delimiter = '\t' if '\t' in header else ';' if ';' in header else ','
    try:
        records = list(csv.reader(StringIO(text), delimiter=delimiter, strict=True))
    except csv.Error as error:
        raise ValueError(f'Invalid CSV: {error}') from error
    names = [x.strip() for x in records[0]]
    if not all(names) or len(set(names)) != len(names):
        raise ValueError('Every column needs a unique, nonempty header.')
    rows = []
    for index, row in enumerate(records[1:], 2):
        if not row or all(not value.strip() for value in row):
            continue
        if len(row) != len(names):
            raise ValueError(f'CSV row {index}: expected {len(names)} columns, found {len(row)}.')
        rows.append([x.strip() for x in row])
    frame = pd.DataFrame(rows, columns=names)
    # Decimal commas are accepted with semicolon/tab separation. Thousands
    # separators are deliberately unsupported, avoiding ambiguous numbers.
    if delimiter != ',':
        frame = frame.apply(lambda col: col.str.replace(',', '.', regex=False))
    return frame


def numeric_columns(frame, required, optional=()):
    missing = set(required)-set(frame.columns)
    if missing:
        raise ValueError('Missing columns: '+', '.join(sorted(missing))+'. Download a template or map your headers.')
    data = frame.copy().reset_index(drop=True)
    for name in (*required, *optional):
        if name not in data:
            data[name] = np.nan
        blank = data[name].isna() | data[name].astype(str).str.strip().eq('')
        numbers = pd.to_numeric(data[name].mask(blank), errors='coerce')
        invalid = (~np.isfinite(numbers)) & (~blank if name in optional else True)
        if invalid.any():
            row = int(np.flatnonzero(invalid)[0])+2
            raise ValueError(f'Row {row}, column {name}: enter a finite number'+(' or leave it blank.' if name in optional else '.'))
        data[name] = numbers.astype(float)
    return data


def integer_column(data, name, minimum=1, maximum=None):
    values = data[name].to_numpy()
    bad = (values != np.floor(values)) | (values < minimum)
    if maximum is not None:
        bad |= values > maximum
    if bad.any():
        row = int(np.flatnonzero(bad)[0])+2
        raise ValueError(f'Row {row}, column {name}: expected an integer from {minimum}'+(f' to {maximum}.' if maximum is not None else ' upwards.'))
    data[name] = data[name].astype(int)


def nuclear_tables(level_frame, element_frame):
    """Convert editable spreadsheet tables to the solver's immutable model records."""
    levels = numeric_columns(level_frame, ('level','spin','energy_mev','parity'), ('k',))
    if levels.empty:
        raise ValueError('Add at least a ground-state level.')
    integer_column(levels, 'level')
    integer_column(levels, 'parity', -1, 1)
    if not np.array_equal(levels.level, np.arange(1, len(levels)+1)):
        raise ValueError('Level numbers must be consecutive and ordered, beginning at 1.')
    elements = numeric_columns(element_frame, ('initial','final','value','lambda'))
    for name in ('initial','final'):
        integer_column(elements, name, maximum=len(levels))
    integer_column(elements, 'lambda', 1, 4)
    states = tuple(Level(row.spin, row.energy_mev, int(row.parity), 0. if pd.isna(row.k) else row.k)
                   for row in levels.itertuples())
    couplings = tuple(MatrixElement(int(row['initial'])-1,int(row['final'])-1,row['value'],int(row['lambda']))
                      for _,row in elements.iterrows())
    return states, couplings


def table_texts(reaction):
    """The levels and matrix-elements CSV tables describing `reaction` (inverse of nuclear_tables)."""
    levels = ['level,spin,energy_mev,parity,k', *(f'{i+1},{x.spin:g},{x.energy:.10g},{x.parity},{x.k:g}'
                                                  for i, x in enumerate(reaction.levels))]
    elements = ['initial,final,value,lambda', *(f'{m.initial+1},{m.final+1},{m.value:.10f},{m.multipolarity}'
                                                for m in reaction.elements)]
    return '\n'.join(levels)+'\n', '\n'.join(elements)+'\n'


def reaction_text(reaction):
    """Export a complete legacy input (excitation selection remains a UI setting)."""
    lines = [reaction.title,str(len(reaction.levels)),f'{reaction.projectile_z} {reaction.projectile_a}',
             f'{reaction.target_z} {reaction.target_a}',f'{reaction.energy_lab:.16g}',
             f'{reaction.theta_min:g} {reaction.theta_max:g} {reaction.theta_step:g}']
    lines += [f'{i+1} {x.spin:g} {x.energy:.16g} {x.parity} {x.k:g}' for i,x in enumerate(reaction.levels)]
    lines += [f'{x.initial+1} {x.final+1} {x.value:.16g} {x.multipolarity}' for x in reaction.elements]
    return '\n'.join(lines)+'\n'
