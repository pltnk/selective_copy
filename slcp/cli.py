"""
This module is a part of slcp command line application
and is licensed under the MIT License.
Copyright (c) 2019 Kirill Plotnikov
GitHub: https://github.com/pltnk/selective_copy
PyPi: https://pypi.org/project/slcp/
"""


import os
from argparse import ArgumentParser


class ArgParser:
    """Command line arguments parser."""

    def __init__(self):
        """Parse command line arguments, format given extensions and arguments containing paths."""
        self.parser = ArgumentParser(
            usage="slcp ext [ext ...] [-s SRC] [-d DST] [-sc | -dc] "
            "[-p] [-i] [-m] [-e FILE [FILE ...]] [-l] [-h]",
            description="Copy all files with given extensions from a directory and its subfolders "
            "to another directory. "
            "A destination folder must be outside of a source folder.",
        )
        self.parser.add_argument(
            "ext",
            nargs="+",
            help="one or more extensions, enter without a dot, separate by spaces",
        )
        self.parser.add_argument(
            "-s", "--source", help="source folder path", metavar="SRC"
        )
        self.parser.add_argument(
            "-d", "--dest", help="destination folder path", metavar="DST"
        )
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "-sc",
            "--srccwd",
            action="store_true",
            help="use current working directory as a source",
        )
        group.add_argument(
            "-dc",
            "--dstcwd",
            action="store_true",
            help="use current working directory as a destination",
        )
        self.parser.add_argument(
            "-p",
            "--preserve",
            action="store_true",
            help="preserve source folder structure",
        )
        self.parser.add_argument(
            "-i",
            "--invert",
            action="store_true",
            help="process only files without given extensions",
        )
        self.parser.add_argument(
            "-m", "--move", action="store_true", help="move files instead of copying"
        )
        self.parser.add_argument(
            "-e",
            "--exclude",
            nargs="+",
            help="exclude certain files from processing",
            metavar="FILE",
        )
        self.parser.add_argument(
            "-l",
            "--log",
            action="store_true",
            help="create and save log to the destination folder",
        )
        self.args = self.parser.parse_args()
        self.args.ext = tuple(set(f".{item}" for item in self.args.ext))
        if self.args.source:
            self.args.source = os.path.normpath(self.args.source.strip())
        if self.args.dest:
            self.args.dest = os.path.normpath(self.args.dest.strip())
        self.args.exclude = (
            tuple(set(self.args.exclude)) if self.args.exclude else tuple()
        )
