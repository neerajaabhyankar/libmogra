import os
import argparse
import io
from PIL import Image
import libmogra as lm
from libmogra.raagfinder.parse import RAAG_DB, RAAG_DB_BY_SWAR, best_match, print_table


IMAGE_SCALE = 1.5


def info(raag, show_tonnetz=False):
    raag_name = raag.lower()
    if raag_name not in RAAG_DB:
        raag_name = best_match(raag_name)

    print_table(RAAG_DB[raag_name])

    if show_tonnetz != "none":
        tn = lm.tonnetz.Tonnetz()
        figure = tn.plot_raag(raag_name)
        if figure is None:
            return

        if show_tonnetz == "browser":
            figure.show(scale=IMAGE_SCALE)
        elif show_tonnetz == "window":
            image_buffer = io.BytesIO()
            figure.write_image(image_buffer, format="png", scale=IMAGE_SCALE)
            image_buffer.seek(0)
            image = Image.open(image_buffer)
            image.show()
        elif os.path.exists("/".join(show_tonnetz.split("/")[:-1])):
            figure.write_image(show_tonnetz, scale=IMAGE_SCALE)
        else:
            print("invalid display arg passed to --tonnetz")


def search(swar):
    swar_set = [char for char in swar if char in lm.datatypes.Swar._member_names_]
    swar_set = sorted(swar_set, key=lambda x: lm.datatypes.Swar[x].value)
    swar_set = list(dict.fromkeys(swar_set))
    print("Looking for raags with notes", " ".join(swar_set), " ...")
    results = RAAG_DB_BY_SWAR.get(tuple(swar_set), [])
    if len(results) == 0:
        print("... none found.")
    for res in results:
        print_table(RAAG_DB[res])


def main():
    parser = argparse.ArgumentParser(
        # description="A CLI tool for looking up basic Raag information"
    )
    subparsers = parser.add_subparsers(dest="function")

    # info subparser
    parser_info = subparsers.add_parser(
        "info", help="Look up basic information by Raag"
    )
    parser_info.add_argument("raag", type=str, help="Raag name")
    parser_info.add_argument(
        "--tonnetz",
        default="none",
        help="How to display the tonnetz diagram (none/window/browser/save_path)",
    )

    # search subparser
    parser_search = subparsers.add_parser(
        "search", help="Find a Raag from a set of notes"
    )
    parser_search.add_argument(
        "swar",
        type=str,
        help="Provide a set of notes among SrRgGmMPdDnN (m = shuddha, M = teevra)",
    )

    args = parser.parse_args()

    if args.function == "info":
        info(args.raag, args.tonnetz)

    if args.function == "search":
        search(args.swar)


"""
Run this as follows:
$ mogra Bairagi
"""
