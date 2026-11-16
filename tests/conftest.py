from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coulex import parse_input

@pytest.fixture
def magnesium():
    """The built-in 22Mg + 104Pd example (literature data); many tests use only its kinematics."""
    return parse_input((ROOT/'examples/22Mg_104Pd_literature.txt').read_text())
