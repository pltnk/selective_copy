"""
This module is a part of slcp command line application
and is licensed under the MIT License.
Copyright (c) 2019 Kirill Plotnikov
GitHub: https://github.com/pltnk/selective_copy
PyPi: https://pypi.org/project/slcp/
"""


import os
import shutil
import sys
from tkinter.filedialog import askdirectory

from slcp.log import Log


class Handler:
    """File processing handler."""

    def __init__(self, args):
        """
        Initialize Handler object according to arguments given in the command line.
        :param args: argparse.Namespace. Command line arguments.
        """
        self.args = args
        self.source = self.select_source()
        self.destination = self.select_destination()
        self.log = Log(args, self.destination)
        self.todo = self.get_todo()
        self.total = len(self.todo)
        self.action = shutil.move if args.move else shutil.copy
        self.excluded = ", ".join(args.exclude)
        self.processed = 0
        self.message = (
            f'{"Moving" if args.move else "Copying"} '
            f'{self.total} file{"s" if self.total > 1 else ""} '
            f'{"without" if args.invert else "with"} '
            f'{", ".join(args.ext)} extension{"s" if len(args.ext) > 1 else ""} '
            f"from {self.source} to {self.destination}"
            f'{" preserving source folder structure" if args.preserve else ""}'
            f'{f", excluding {self.excluded}" if len(args.exclude) > 0 else ""}'
        )
        try:
            self.check_for_errors()
        except Exception as e:
            self.log.logger.error(f"{e}\n")
            self.log.close()
            sys.exit(e)

    def select_source(self):
        """
        Check if the source path is in the command line arguments,
        if not ask user for input using filedialog.
        :return: str. Source folder path.
        """
        if self.args.srccwd:
            source = os.getcwd()
        else:
            if self.args.source is None:
                print("Choose a source path.")
                source = os.path.normpath(askdirectory())
                print(f"Source path: {source}")
            else:
                source = self.args.source
        return source

    def select_destination(self):
        """
        Check if the destination path is in the command line arguments,
        if not ask user for input using filedialog.
        If the destination path in arguments does not exist create it.
        :return: str. Destination folder path.
        """
        if self.args.dstcwd:
            destination = os.getcwd()
        else:
            if self.args.dest is None:
                print("Choose a destination path.")
                destination = os.path.normpath(askdirectory())
                print(f"Destination path: {destination}")
            else:
                destination = self.args.dest
                if not os.path.exists(destination):
                    os.makedirs(destination)
        return destination

    def get_todo(self):
        """
        Create a to-do list where each sublist represents one file and contains
        source and destination paths for this file.
        :return: list of list of str. To-do list.
        """
        todo_list = []
        try:
            os.chdir(self.source)
            for foldername, _, filenames in os.walk(self.source):
                if self.args.preserve:
                    path = os.path.join(
                        self.destination,
                        f'{"not_" if self.args.invert else ""}'
                        f'{"_".join(self.args.ext).replace(".", "")}'
                        f"_{os.path.basename(self.source)}",
                        os.path.relpath(foldername),
                    )
                for filename in filenames:
                    if (
                        filename.endswith(self.args.ext) ^ self.args.invert
                    ) and filename not in self.args.exclude:
                        if self.args.preserve:
                            todo_list.append(
                                [
                                    os.path.join(foldername, filename),
                                    os.path.join(path, filename),
                                ]
                            )
                        else:
                            todo_list.append(
                                [
                                    os.path.join(foldername, filename),
                                    os.path.join(self.destination, filename),
                                ]
                            )
        except FileNotFoundError:
            pass
        return todo_list

    def check_for_errors(self):
        """Check for errors, raise corresponding Exception if any errors occurred."""
        if not os.path.exists(self.source):
            raise Exception(f"Error: Source path {self.source} does not exist.")
        elif self.total == 0:
            raise Exception(
                f'Error: There are no {", ".join(self.args.ext)} files in {self.source}.'
            )
        elif os.path.commonpath([self.source, self.destination]) == self.source:
            raise Exception(
                f"Error: A destination folder must be outside of source folder. "
                f"Paths given: source - {self.source} | destination - {self.destination}."
            )
        else:
            pass

    def process(self):
        """
        Copy or move files according to source and destination paths
        given in self.todo_list. Each item in this list represents one file.
        item[0] - source, item[1] - destination.
        :return: NoneType.
        """
        self._show_progress_bar()
        for item in self.todo:
            if not os.path.exists(os.path.dirname(item[1])):
                os.makedirs(os.path.dirname(item[1]))
            try:
                if not os.path.exists(item[1]):
                    self.log.logger.info(f"{item[0]}")
                    self.action(item[0], item[1])
                else:
                    new_filename = f"{os.path.basename(os.path.dirname(item[0]))}_{os.path.basename(item[1])}"
                    self.log.logger.info(f"*{item[0]} saving it as {new_filename}")
                    self.action(
                        item[0], os.path.join(os.path.dirname(item[1]), new_filename)
                    )
            except Exception as e:
                self.log.logger.error(
                    f"*Unable to process {item[0]}, an error occurred: {e}"
                )
            self.processed += 1
            self._show_progress_bar()

    def _show_progress_bar(self):
        """
        Print progress bar.
        :return: NoneType.
        """
        try:
            term_width = os.get_terminal_size(0)[0]
        except OSError:
            term_width = 80
        length = term_width - (len(str(self.total)) + 33)
        percent = round(100 * (self.processed / self.total))
        filled = int(length * self.processed // self.total)
        bar = f'|{"=" * filled}{"-" * (length - filled)}|' if term_width > 50 else ""
        suffix = (
            f"Files left: {self.total - self.processed} "
            if self.processed < self.total
            else "Done, log saved"
            if self.args.log
            else "Done           "
        )
        print(f"\rProgress: {bar} {percent}% {suffix}", end="\r", flush=True)
        if self.processed == self.total:
            print()
