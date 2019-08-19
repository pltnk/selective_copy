# slcp - command line application that copies all files with given extensions
# from a directory and its subfolders to another directory.
# Allows to preserve a source folder structure, to process only files without given extensions,
# to move files instead of copying, to exclude certain files from processing and to create a log if necessary.
# Opens a filedialog if source and/or destination are not given in the command line.
# Creates folders in destination if they don't exist.
# This project is licensed under the MIT License.
# Copyright (c) 2019 Kirill Plotnikov
# GitHub: https://github.com/pltnk/selective_copy
# PyPi: https://pypi.org/project/slcp/


from .cli import ArgParser
from .process import Handler


def main():
    """Process files according to the command line arguments."""
    parser = ArgParser()
    handler = Handler(parser.args)
    print(handler.message)
    handler.log.logger.info(handler.message)
    handler.process()
    handler.log.logger.info(f"Process finished\n")
    handler.log.close()


if __name__ == "__main__":
    main()
