import libmogra.raagdb as raagdb


def test_parse():
    assert raagdb["bairagi"]["vaadi"] == "m", "Error in database"
    assert len(raagdb["basant"]["mukhyanga"]) > 4
