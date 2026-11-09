"""
The raag database, merged from:

    names.json      the master list: which raags are in the database, and what they are
                    called (display name, alternative names/spellings, Marathi, Hindi).
                    Keyed by the display name slugified; "tanarang_key" links a raag
                    whose tanarang key slugifies to something else
    tanarang.json   scraped from tanarang.com + notebook cleanup; never edited by hand
    extras.json     hand-added raags, same fields as tanarang entries (optional)

into raags.pkl. After editing any of these, rebuild it with

    python -m libmogra.raagdb
"""

import json
import os
import pickle
import re


RAAGDB_DIR = os.path.dirname(__file__)
NAMES_FILE = "names.json"
SOURCE_FILES = ["tanarang.json", "extras.json"]
PICKLE_PATH = os.path.join(RAAGDB_DIR, "raags.pkl")


def read_json(filename):
    path = os.path.join(RAAGDB_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def slugify(name):
    """ "Dhanashree (Bhairavi Ang)" -> "dhanashree-bhairavi-ang" """
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def build():
    names = read_json(NAMES_FILE)

    # source entries by their own key, and by that key slugified
    sources = {}
    for filename in SOURCE_FILES:
        for key, entry in read_json(filename).items():
            assert key not in sources, f"{key} is defined in more than one source"
            sources[key] = entry
    slugs = {slugify(key): key for key in sources}

    # names.json keys are slugs of the display names; where that isn't the source's key
    # slugified (a raag renamed from tanarang's), "tanarang_key" says which entry to use
    raag_db = {}
    for key, entry_names in names.items():
        entry_names = dict(entry_names)
        source_key = entry_names.pop("tanarang_key", slugs.get(key))
        assert source_key in sources, f"no source data for {key}"
        source = {field: value for field, value in sources[source_key].items() if field != "name"}
        raag_db[key] = {"name": key, **entry_names, **source}
    return raag_db


def write_pickle():
    raag_db = build()
    with open(PICKLE_PATH, "wb") as fp:
        pickle.dump(raag_db, fp)
    return raag_db


def read_pickle():
    with open(PICKLE_PATH, "rb") as fp:
        return pickle.load(fp)


RAAG_DB = read_pickle() if os.path.exists(PICKLE_PATH) else build()
