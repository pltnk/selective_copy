# selective_copy
Simple command line application that copies all files with given extension from a directory and its subfolders to an another directory. Inspired by the task from [Chapter 9 of Automate the Boring Stuff](https://automatetheboringstuff.com/chapter9/)\ 
Allows to preserve source folder structure and to create a log if necessary.\
Opens a filedialog if source and/or destination are not given in the command line.\
Creates folders in destination if they don't exist.

Usage:\
Positional arguments:\
ext                         Extension for the files to copy, enter without a dot.

Optional arguments:\
-s SOURCE, --source SOURCE  Source path.\
-d DEST, --dest DEST        Destination path.\
-p, --preserve              Preserve source folder structure.\
-l, --log                   Create and save log to the destination folder.\
-h, --help                  Show this help message and exit.
