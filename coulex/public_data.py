"""Energy levels from public nuclear data: IAEA Nuclear Data Services (LiveChart of Nuclides, ENSDF evaluations).

Only level energies and spins are retrieved. Matrix elements are not part of the public level data and
must be entered by the user. Nothing here is fetched unless the user presses the load button.
"""
from dataclasses import dataclass
import csv
from datetime import date
import re
from io import StringIO
import urllib.error
import urllib.parse
import urllib.request
import pandas as pd

SERVICE = 'https://nds.iaea.org/relnsd/v1/data'
SERVICE_HOST = 'nds.iaea.org'
SOURCE = 'IAEA Nuclear Data Services, LiveChart of Nuclides (ENSDF adopted levels)'
ELEMENTS = ('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr '
            'Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb '
            'Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf '
            'Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og').split()
MAX_BYTES = 2_000_000
TIMEOUT_SECONDS = 20
SPIN_PATTERN = re.compile(r'^(\d+)(?:/(\d+))?([+-])$')


class PublicDataError(RuntimeError):
    """The public service could not be used; the message says why."""


@dataclass(frozen=True)
class LoadedLevels:
    nuclide: str
    levels: pd.DataFrame        # columns: level, spin, energy_mev, parity, k
    skipped: tuple[tuple[str, str], ...]   # (entry label, reason code: 'energy' or 'spin')
    retrieved: str              # ISO date of retrieval


def nuclide_symbol(z: int, a: int) -> str:
    """Nuclide in the service's notation, e.g. 12, 22 -> '22Mg'. Raises ValueError for impossible values."""
    if not (1 <= z <= len(ELEMENTS)) or a < z or a > 400:
        raise ValueError(f'Z = {z} and A = {a} do not describe a nucleus.')
    return f'{a}{ELEMENTS[z-1]}'


def _parse_spin(text: str):
    """(spin, parity) for a single unambiguous value such as '2+', '(4+)' or '3/2-'; otherwise None."""
    cleaned = re.sub(r'[()\[\]#@ ]', '', text)
    match = SPIN_PATTERN.match(cleaned)
    if not match:
        return None
    numerator, denominator, sign = match.groups()
    spin = int(numerator) / int(denominator or 1)
    return spin, 1 if sign == '+' else -1


def parse_levels(text: str, nuclide: str, max_energy_mev: float, retrieved: str | None = None) -> LoadedLevels:
    """Convert the service's CSV into the app's level table. Entries with uncertain energy or spin are skipped
    and listed, never guessed."""
    rows = list(csv.DictReader(StringIO(text)))
    if not rows:
        raise PublicDataError(f'no level data for {nuclide} in the service; check Z and the mass number A')
    loaded, skipped = [], []
    for row in rows:
        label = f"{row.get('energy') or '—'} keV ({row.get('jp') or 'spin unknown'})"
        energy_text = (row.get('energy') or '').strip()
        try:
            if '?' in energy_text:
                raise ValueError(energy_text)
            energy = float(energy_text) / 1000.
        except ValueError:
            skipped.append((label, 'energy'))
            continue
        if energy > max_energy_mev:
            continue
        parsed = _parse_spin(row.get('jp') or '')
        if parsed is None:
            skipped.append((label, 'spin'))
            continue
        spin, parity = parsed
        loaded.append((energy, spin, parity))
    if not loaded or loaded[0][0] != 0.:
        raise PublicDataError(f'The ground state of {nuclide} (0 MeV, unique spin) was not found.')
    levels = pd.DataFrame([{'level': i+1, 'spin': spin, 'energy_mev': energy, 'parity': parity, 'k': 0.}
                           for i, (energy, spin, parity) in enumerate(sorted(loaded))])
    return LoadedLevels(nuclide, levels, tuple(skipped), retrieved or date.today().isoformat())


def fetch_levels_csv(nuclide: str) -> str:
    """Download the level list for one nuclide from the IAEA service (HTTPS only, size and time limited)."""
    match = re.fullmatch(r'(\d{1,3})([A-Z][a-z]?)', nuclide)
    if not match or match.group(2) not in ELEMENTS:
        raise PublicDataError(f'{nuclide} is not a valid nuclide name.')
    query = urllib.parse.urlencode({'fields': 'levels', 'nuclides': nuclide})
    url = f'{SERVICE}?{query}'
    if urllib.parse.urlsplit(url).hostname != SERVICE_HOST:
        raise PublicDataError('Unexpected service address.')
    request = urllib.request.Request(url, headers={'User-Agent': 'Coulomb-Excitation-Lab'})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BYTES + 1)
    except (urllib.error.URLError, OSError) as error:
        raise PublicDataError(str(getattr(error, 'reason', error))) from error
    if len(body) > MAX_BYTES:
        raise PublicDataError('The response is larger than expected.')
    text = body.decode('latin-1')
    if not text.strip() or text.strip() == '2':
        raise PublicDataError(f'no level data for {nuclide} in the service; check Z and the mass number A')
    return text
