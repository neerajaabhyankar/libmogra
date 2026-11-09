import unicodedata
from libmogra.raagdb import RAAG_DB as raagdb, build, read_json, slugify, NAMES_FILE
from libmogra.raagfinder.parse import best_match, fold


def test_pickle_is_up_to_date():
    assert raagdb == build(), "raags.pkl is stale -- run `python -m libmogra.raagdb`"


def test_names_master_list():
    assert list(raagdb) == list(read_json(NAMES_FILE))
    for key, entry in raagdb.items():
        assert entry["name"] == key == slugify(entry["display_name"])
        assert "tanarang_key" not in entry
        assert entry["display_name"]
        assert entry["mr_names"] and entry["hi_names"]
        for name in entry["mr_names"] + entry["hi_names"]:
            assert name == unicodedata.normalize("NFC", name), f"{key}: {name} is not NFC"


def test_aliases_unique():
    seen = {}
    for key, entry in raagdb.items():
        aliases = {fold(a) for a in [key, entry["display_name"]] + entry["alt_names"]}
        for alias in aliases:
            assert seen.setdefault(alias, key) == key, f"{alias} names {seen[alias]} and {key}"


def test_best_match():
    assert best_match("bairagi") == "bairagi"
    assert best_match("Bhinna Shadja") == "bhinna-shadja"
    assert best_match("kaushik dhwani") == "bhinna-shadja"
    assert best_match("Nat Bhairav") == "nat-bhairav"
    assert best_match("vrindavani sarang") == "vrindavani-sarang"
    assert best_match("chhayanat") == "chhayanat"
    assert best_match("bheempalas") == "bheempalasi"
    assert best_match("Nut-Bhairav") == "nat-bhairav"
    assert best_match("abhogi kanada") == "abhogi"
    assert best_match("dhanashree (bhairavi ang)") == "dhanashree-bhairavi-ang"
    assert best_match("bhinna shadaj") == "bhinna-shadja"
