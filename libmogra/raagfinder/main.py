import argparse
import libmogra as lm
from libmogra.raagfinder.parse import RAAG_DB, RAAG_DB_BY_SWAR, best_match, print_table


def info(raag):
    raag_name = raag.lower()
    if raag_name not in RAAG_DB:
        raag_name = best_match(raag_name)
    
    print_table(RAAG_DB[raag_name])
    

def search(swar):
    swar_set = [char for char in swar if char in lm.datatypes.Swar._member_names_]
    swar_set = sorted(swar_set, key=lambda x: lm.datatypes.Swar[x].value)
    swar_set = list(dict.fromkeys(swar_set))
    print("Looking for raags with notes", " ".join(swar_set), " ...")
    results = RAAG_DB_BY_SWAR[tuple(swar_set)]
    for res in results:
        print_table(RAAG_DB[res])


def main():
    parser = argparse.ArgumentParser(
        # description="A CLI tool for looking up basic Raag information"
    )
    subparsers = parser.add_subparsers(dest="function")

    # info subparser
    parser_info = subparsers.add_parser("info", help="Look up basic information by Raag")
    parser_info.add_argument("raag", type=str, help="Raag name")

    # search subparser
    parser_search = subparsers.add_parser("search", help="Find a Raag from a set of notes")
    parser_search.add_argument("swar", type=str, help="Provide a set of notes among SrRgGmMPdDnN (m = shuddha, M = teevra)")

    args = parser.parse_args()

    if args.function == "info":
        info(args.raag)
    
    if args.function == "search":
        search(args.swar)


"""
Run this as follows:
$ mogra Bairagi
"""