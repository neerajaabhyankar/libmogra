from libmogra.raagfinder import parse as parse_raagdb

raags_db, _ = parse_raagdb.read_pickle()

assert raags_db["bairagi"]["vaadi"] == "m", "Error in database"