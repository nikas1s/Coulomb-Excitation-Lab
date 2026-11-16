"""English/Greek interface text.

Short strings are looked up by their English text (``t``); long instruction
pages come from :mod:`coulex.i18n_docs` (``doc``). Library errors stay in
English inside the numerical package and are translated for display
(``error_text``). A test checks that every ``t('…')`` literal in the code has
a Greek translation.
"""
import re
from .i18n_el import EL, ERRORS_EL
from .i18n_docs import DOCS

LANGUAGES = {'en': 'English', 'el': 'Ελληνικά'}
LANGUAGE_KEY = 'lang'


def current():
    try:
        import streamlit as st
        value = st.session_state.get(LANGUAGE_KEY, 'en')
    except Exception:  # outside a Streamlit run (scripts, tests)
        return 'en'
    return value if value in LANGUAGES else 'en'


def greek():
    return current() == 'el'


def t(text, **values):
    """Translate an English interface string; `values` fill {placeholders}."""
    result = EL.get(text, text) if greek() else text
    return result.format(**values) if values else result


def doc(key, **values):
    entry = DOCS[key]
    result = entry.get(current(), entry['en'])
    return result.format(**values) if values else result


def error_text(error):
    """Display text for a ValueError/RuntimeError raised by the numerical package."""
    message = str(error)
    if not greek():
        return message
    return _translate_error(message)


def _translate_error(message):
    if message in EL:
        return EL[message]
    for pattern, template in ERRORS_EL:
        match = re.fullmatch(pattern, message, flags=re.S)
        if match:
            groups = [_translate_error(g) if g and len(g) > 12 else g for g in match.groups()]
            return template.format(*groups)
    return message
