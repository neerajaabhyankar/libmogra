from libmogra.tonnetz import EFGenus, Tonnetz


def test_tonnetz():
    g1 = EFGenus.from_list([3, 3, 5])
    assert len(g1.primes) == 2
    assert g1.powers == [2, 1]

    tn = Tonnetz(g1)
    assert len(set(tn.node_names)) == 12
