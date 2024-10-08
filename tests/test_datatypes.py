from libmogra import datatypes


def test_parse_shruti():
    pa = datatypes.Shruti(num_denom=(3, 2))
    assert pa.swar == "P"
    assert pa.frequency == 1.5


def test_parse_samooha():
    bhoop_aroha = datatypes.Samooha("SRGPDS`")
    assert len(bhoop_aroha.list) == 6
