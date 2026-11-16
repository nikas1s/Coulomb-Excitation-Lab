"""The solver against published Coulomb-excitation theory and tables (see coulex/literature.py)."""
from dataclasses import replace
import math
import numpy as np
import pytest
from scipy.integrate import quad
from coulex import CoupledChannels, Level, MatrixElement, SolverSettings
from coulex.literature import (AW60_TABLE5, aw60_probabilities, benchmark_suite,
                               diagonal_from_quadrupole, first_order_probability, orbital_integral, rotor_for_q,
                               rotor_matrix_element, rotor_q0_from_be2, spectroscopic_quadrupole, strength_parameter)

TIGHT = SolverSettings(rtol=1e-11, atol=1e-15)


def test_full_benchmark_suite_passes(magnesium):
    rows = benchmark_suite(magnesium)
    assert len(rows) == 12
    failed = [(row.group, row.label, row.difference) for row in rows if not row.passed]
    assert not failed, failed


@pytest.mark.filterwarnings('ignore::scipy.integrate.IntegrationWarning')
def test_contour_shift_equals_real_axis_integral():
    """Cauchy: the shifted path used for ξ > 0 equals the direct oscillatory integral."""
    for lam, mu, theta, xi in [(2, 0, 90., .4), (2, 2, 150., .3), (1, 1, 60., .2), (3, -1, 120., .5)]:
        eps = 1/math.sin(math.radians(theta)/2)
        root = math.sqrt(eps*eps-1)
        f = lambda w: (np.exp(1j*xi*(eps*np.sinh(w)+w))*(np.cosh(w)+eps+1j*root*np.sinh(w))**mu
                       / (eps*np.cosh(w)+1)**(lam+mu))
        direct = complex(*(quad(lambda w: g(f(w)), -14, 14, limit=4000, epsabs=1e-13)[0] for g in (np.real, np.imag)))
        # The direct oscillatory quadrature is good to ~1e-8; a wrong path would differ by O(0.1).
        assert orbital_integral(lam, mu, theta, xi) == pytest.approx(direct, abs=1e-7)


def test_head_on_orbital_integral_closed_form():
    # ∫ (1 + cosh w)^-2 dw = 2/3 at θ = 180°, ξ = 0.
    assert orbital_integral(2, 0, 180., 0.) == pytest.approx(2/3, rel=1e-12)


@pytest.mark.parametrize('q', sorted(AW60_TABLE5))
def test_solver_matches_aw60_closed_form(magnesium, q):
    # The printed Tables 4 and 5 are checked by the benchmark suite; the exact formula is far more precise.
    rotor = rotor_for_q(magnesium, q, 22)
    probabilities = CoupledChannels(rotor).solve(180., TIGHT).probabilities
    assert sum(probabilities) == pytest.approx(1, abs=1e-9)
    exact = aw60_probabilities(q, [level.spin for level in rotor.levels])
    np.testing.assert_allclose(probabilities, exact, atol=2e-5)


@pytest.mark.parametrize('lam,spin,parity', [(1, 1., -1), (2, 2., 1), (3, 3., -1), (4, 4., 1)])
def test_weak_coupling_limit_is_first_order_theory(magnesium, lam, spin, parity):
    model = replace(magnesium, dipole_strength=0., levels=(Level(0., 0.), Level(spin, .8, parity)),
                    elements=(MatrixElement(0, 1, 2e-4, lam),))
    for theta in (45., 135.):
        expected = first_order_probability(model, theta, 1)
        assert CoupledChannels(model).solve(theta, TIGHT).probabilities[1] == pytest.approx(expected, rel=1e-4)


def test_first_order_probability_scales_with_b_value(magnesium):
    model = replace(magnesium, dipole_strength=0., levels=(Level(0., 0.), Level(2., 1.)),
                    elements=(MatrixElement(0, 1, .01, 2),))
    double = replace(model, elements=(MatrixElement(0, 1, .02, 2),))
    assert first_order_probability(double, 90., 1) == pytest.approx(4*first_order_probability(model, 90., 1))


def test_head_on_first_order_equals_chi_squared(magnesium):
    model = replace(magnesium, dipole_strength=0., levels=(Level(0., 0.), Level(2., 0.)),
                    elements=(MatrixElement(0, 1, .01, 2),))
    assert first_order_probability(model, 180., 1) == pytest.approx(strength_parameter(model, 1, 2, .01)**2, rel=1e-10)


def test_rotor_relations():
    q0 = rotor_q0_from_be2(3.4611)
    assert rotor_matrix_element(0, 2, q0)**2 == pytest.approx(3.4611)
    # Q(2+) = −2/7 Q0 for a K = 0 rigid rotor.
    assert spectroscopic_quadrupole(2, rotor_matrix_element(2, 2, q0)) == pytest.approx(-2/7*q0)
    assert spectroscopic_quadrupole(2, diagonal_from_quadrupole(2, -.1)) == pytest.approx(-.1)


@pytest.mark.parametrize('excitation,a,z', [('projectile',22,12), ('target',104,46)])
def test_polarization_uses_excited_nucleus_orce_equation_4_and_footnote_1(magnesium,excitation,a,z):
    # Orce, arXiv:1510.04087 Eq. (4) and footnote 1, with kappa=1.
    # Physical projectile lab frame: Ecm = E_lab*104/(22+104) MeV.
    reaction=replace(magnesium,excitation=excitation)
    expected=.005*magnesium.energy_lab*104/(22+104)*a/z**2
    assert reaction.polarization==pytest.approx(expected,rel=1e-14)
    assert replace(reaction,dipole_strength=0.).polarization==0.
    assert replace(reaction,dipole_strength=.01).polarization==pytest.approx(2*expected)


def test_reference_polarization_is_explicit_and_separate(magnesium):
    assert magnesium.polarization_convention=='standard'
    reference=replace(magnesium,polarization_convention='reference')
    assert reference.polarization==pytest.approx(magnesium.polarization*104/22)
    with pytest.raises(ValueError,match='Unknown polarization'):
        replace(magnesium,polarization_convention='invalid')
