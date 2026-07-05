import pytest
from fractions import Fraction
from libmogra.tonnetz import EFGenus, Tonnetz


def test_tonnetz():
    g1 = EFGenus.from_list([3, 3, 5])
    assert len(g1.primes) == 2
    assert g1.powers == [2, 1]

    tn = Tonnetz(g1)
    assert len(set(tn.node_names)) == 12

    # ensure that tn.plot_raag() returns an assertion error
    with pytest.raises(AssertionError):
        err = tn.plot_raag("all")


def test_ratios():
    g1 = EFGenus.from_list([3, 3, 5])
    tn = Tonnetz(g1)

    assert tn.coord_to_ratio((0, 0)) == 1
    assert tn.coord_to_ratio((0, 1)) == Fraction(5, 4)
    assert tn.coord_to_ratio((1, -1)) == Fraction(6, 5)

    assert tn.ratio_to_coord(1) == (0, 0)
    assert tn.ratio_to_coord(Fraction(5, 4)) == (0, 1)
    assert tn.ratio_to_coord(Fraction(48, 9)) == (-1, 0)

    tn.set_color_scheme("daylight")
    assert tn.get_node_color((0, 0)) == "#2d992d"
    assert tn.get_node_color((-1, -1)) == "#179992"


def test_node_assignments():
    g1 = EFGenus.from_list([3, 3, 5])
    tn = Tonnetz(g1)

    assert tn.node_names[0] == "M"
    assert tn.node_names[7] == "S"
    assert tn.node_names[14] == "M"

    assert tn.node_ratios[0] == Fraction(64, 45)
    assert tn.node_ratios[7] == 1
    assert tn.node_ratios[14] == Fraction(45, 32)

    assert tn.get_swar_options("S") == [(0, 0)]
    assert tn.get_swar_options("M") == [(-2, -1), (2, 1)]
