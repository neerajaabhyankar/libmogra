import json
import os


def read_json():
    with open(os.path.join(os.path.dirname(__file__), "tanarang.json")) as fp:
        return json.load(fp)


RAAG_DB = read_json()
