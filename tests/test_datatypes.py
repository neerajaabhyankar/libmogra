from libmogra.datatypes import Shruti, Samooha, Swar, Saptak, SSwar
from libmogra.datatypes import ratio_to_swar, ratio_to_sswar, ratio_to_swarval


def test_parse_shruti():
    pa = Shruti(num_denom=(3, 2))
    assert pa.swar == "P"
    assert pa.frequency == 1.5


def test_parse_samooha():
    bhoop_aroha = Samooha("SRGPDS`")
    assert len(bhoop_aroha.list) == 6


def test_ratio_to_swar():
    assert ratio_to_swar(1.5) == "P"
    assert ratio_to_swar(2) == "S"
    assert ratio_to_swar(9 / 8) == "R"


def test_ratio_to_sswar():
    assert ratio_to_sswar(1.5) == SSwar.from_classes(Saptak.madhya, Swar.P)
    assert ratio_to_sswar(2) == SSwar.from_classes(Saptak.taara, Swar.S)
    assert ratio_to_sswar(9 / 16) == SSwar.from_classes(Saptak.mandra, Swar.R)


def test_ratio_to_swarval():
    assert ratio_to_swarval(1.5) == 7.019550008653875
    assert ratio_to_swarval(2) == 12
    assert ratio_to_swarval(0.5) == -12
