from libmogra.raagfinder import parse as parse_raagdb


def test_parse():
    raags_db, _ = parse_raagdb.read_pickle()
    assert raags_db["bairagi"]["vaadi"] == "m", "Error in database"
