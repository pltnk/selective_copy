# Selective Copy v0.3.0
[![Python Version](https://img.shields.io/pypi/pyversions/slcp.svg)](https://www.python.org/downloads/release/python-370/)
[![PyPi Version](https://img.shields.io/pypi/v/slcp.svg)](https://pypi.org/project/slcp/)
[![Downloads](https://pepy.tech/badge/slcp)](https://pepy.tech/project/slcp)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bdde9d33956642129d82d219328ad5cc)](https://www.codacy.com/app/pltnk/selective_copy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pltnk/selective_copy&amp;utm_campaign=Badge_Grade)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/pltnk/selective_copy.svg)](https://choosealicense.com/licenses/mit/)

Simple command line application that copies all files with given extensions from a directory and its subfolders to another directory showing progress bar and remaining files counter.\
Allows to preserve a source folder structure, to process only files without given extensions, to move files instead of copying, to exclude certain files from processing and to create a log if necessary.\
Opens a filedialog if source and/or destination are not given in the command line.\
Creates folders in a destination path if they don't exist.

## Installing

```pip install slcp```

## Usage

<pre>
slcp ext [ext ...] [-s SRC] [-d DST] [-sc | -dc] [-p] [-i] [-m] [-e FILE [FILE ...]] [-l] [-h]

Positional arguments:
ext                         One or more extensions of the files to copy. 
                            Enter extensions without a dot and separate by spaces.

Optional arguments:
-s SRC, --source SRC        Source folder path.
-d DST, --dest DST          Destination folder path.
-sc, --srccwd               Use current working directory as a source folder.
-dc, --dstcwd               Use current working directory as a destination folder.
-p, --preserve              Preserve source folder structure.
-i, --invert                Process only files without given extensions.
-m, --move                  Move files instead of copying, be careful with this option.
-e FILE [FILE ...],         Exclude one or more files from processing.
--exclude FILE [FILE ...]   Enter filenames with extensions and separate by spaces.
-l, --log                   Create and save log to the destination folder.
-h, --help                  Show this help message and exit.
</pre>

### Examples

[![asciicast](https://asciinema.org/a/263359.svg)](https://asciinema.org/a/263359?t=2)

## Changelog

### [v0.3.0](https://github.com/pltnk/selective_copy/releases/tag/v0.3.0) - 2019-08-22 
#### Added
- [Black](https://github.com/psf/black) code style

#### Changed
- The code is now divided into separate modules
- Dots that come with extensions are removed from output folder name. 
The reason is that folders with a name starting with a dot are considered as hidden on Linux.
- Log saving indication
- Name of the logfile

#### Fixed
- Issue when paths like /home/user/test and /home/user/test2 were considered as nested which lead to an error.

[Compare with v0.2.1](https://github.com/pltnk/selective_copy/compare/v0.2.1...v0.3.0)

### [v0.2.1](https://github.com/pltnk/selective_copy/releases/tag/v0.2.1) - 2019-07-16 
#### Added
- Changelog

#### Fixed
- Readme of the project on [PyPI](https://pypi.org/project/slcp/) and [GitHub](https://github.com/pltnk/selective_copy)

[Compare with v0.2.0](https://github.com/pltnk/selective_copy/compare/v0.2.0...v0.2.1)

### [v0.2.0](https://github.com/pltnk/selective_copy/releases/tag/v0.2.0) - 2019-07-15 
#### Added
- Support of processing several extensions at once
- --invert option
- --move option
- --exclude option

[Compare with v0.1.0](https://github.com/pltnk/selective_copy/compare/v0.1.0...v0.2.0)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

Inspired by the task from [Chapter 9 of Automate the Boring Stuff](https://automatetheboringstuff.com/chapter9/).
