#! python3
# selective_copy.py - copies all files with given extension from a directory
# and its subfolders to another directory.
# Allows to preserve source folder structure and to create a log if necessary.
# Opens a filedialog if source and/or destination are not given in the command line.
# Creates folders in destination if they don't exist.


import logging, os, shutil, sys
from argparse import ArgumentParser
from tkinter.filedialog import askdirectory


def parse_args():
    """
    Parse command line arguments and format arguments containing paths.
    :return: tuple of (ArgumentParser, Namespace). Parser itself and all arguments.
    """
    parser = ArgumentParser(description='Copy all files with given extension from a directory and its subfolders '
                                        'to another directory. '
                                        'A destination folder must be outside of a source folder.')
    parser.add_argument('ext', help='extension for the files to copy, enter without a dot', type=str)
    parser.add_argument('-s', '--source', help='source path', type=str)
    parser.add_argument('-d', '--dest', help='destination path', type=str)
    parser.add_argument('-p', '--preserve', action='store_true', help='preserve source folder structure')
    parser.add_argument('-l', '--log', action='store_true', help='create and save log to the destination folder')
    args = parser.parse_args()
    if isinstance(args.source, str):
        args.source = os.path.normpath(args.source.strip())
    if isinstance(args.dest, str):
        args.dest = os.path.normpath(args.dest.strip())
    return parser, args


def create_logger(args, destination):
    """
    Create logger and selective_copy.log file
    in the destination folder if logging is turned on
    in command line arguments. If not create only logger.
    :param args: Namespace. Command line arguments.
    :param destination: str. Destination folder path.
    :return: Logger.
    """
    logger = logging.getLogger('selective_copy')
    if args.log:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(f'{destination}\\selective_copy.log', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s', '%d.%m.%Y %H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    else:
        logger.setLevel(logging.CRITICAL)
    return logger


def check_for_errors(source, destination, extension, total):
    """
    Check for errors, return corresponding
    error statement if any errors occurred.
    Otherwise return None.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param extension: str. Extension of files.
    :param total: int. Number of files with extension in source folder.
    :return: str or NoneType. Error statement or None.
    """
    if not os.path.exists(source):
        message = f'Error: Source path {source} does not exist.'
    elif total == 0:
        message = f'Error: There are no {extension} files in {source}.'
    elif source in destination:
        message = f'Error: A destination folder must be outside of source folder. ' \
            f'Paths given: source - {source} | destination - {destination}.'
    else:
        message = None
    return message


def select_source(args):
    """
    Check if the source path is in the command line arguments,
    if not ask user for input using filedialog.
    :param args: Namespace. Command line arguments.
    :return: str. Source folder path.
    """
    if args.source is None:
        print('Choose a source path.')
        source = os.path.normpath(askdirectory())
        print(f'Source path: {source}')
    else:
        source = args.source
    return source


def select_destination(args):
    """
    Check if the destination path is in the command line arguments,
    if not ask user for input using filedialog.
    If the destination path in arguments does not exist create it.
    :param args: Namespace. Command line arguments.
    :return: str. Destination folder path.
    """
    if args.dest is None:
        print('Choose a destination path.')
        destination = os.path.normpath(askdirectory())
        print(f'Destination path: {destination}')
    else:
        destination = args.dest
        if not os.path.exists(destination):
            os.makedirs(destination)
    return destination


def get_total(source, extension):
    """
    Count all appearances of files with given extension
    in the source folder and its subfolders.
    :param source: str. Source folder path.
    :param extension: str. Extension of files.
    :return: int. Total number of said files.
    """
    total = 0
    for f, s, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith(extension):
                total += 1
    return total


# Progress bar is made following the materials from this thread:
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113
def show_progress_bar(total, counter=0, length=80):
    """
    Print progress bar.
    :param total: int. Total number of iterations.
    :param counter: int. Current iteration.
    :param length: int. Length of progress bar in characters.
    :return: NoneType.
    """
    global copied
    percent = round(100 * (counter / total))
    filled_length = int(length * counter // total)
    bar = '=' * filled_length + '-' * (length - filled_length)
    if counter < total:
        suffix = f'Files left: {total - counter} '
    else:
        suffix = 'Done           '
    print(f'\rProgress: |{bar}| {percent}% {suffix}', end='\r', flush=True)
    copied += 1
    if counter == total:
        print()


def copy(source, destination, extension):
    """
    Copy all files with extension from source folder and its subfolders
    to the destination folder.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param extension: str. Extension of the files to copy.
    :return: NoneType.
    """
    show_progress_bar(total)
    for foldername, subfolders, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith(extension):
                if not os.path.exists(os.path.join(destination, filename)):
                    logger.info(f'{filename} from {foldername}')
                    shutil.copy(os.path.join(foldername, filename), os.path.join(destination, filename))
                else:
                    new_filename = f'{os.path.basename(foldername)}_{filename}'
                    logger.info(f'{filename} from {foldername} and saving it as {new_filename}')
                    shutil.copy(os.path.join(foldername, filename), os.path.join(destination, new_filename))
                show_progress_bar(total, copied)


def copy_with_structure(source, destination, extension):
    """
    Copy all files with extension from source folder and its subfolders
    to the destination folder preserving source folder structure.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param extension: str. Extension of the files to copy.
    :return: NoneType.
    """
    show_progress_bar(total)
    for foldername, subfolders, filenames in os.walk(source):
        path = os.path.join(destination, f'{extension} from {os.path.basename(source)}', os.path.relpath(foldername))
        for filename in filenames:
            if filename.endswith(extension):
                if not os.path.exists(path):
                    os.makedirs(path)
                if not os.path.exists(os.path.join(path, filename)):
                    logger.info(f'{filename} from {foldername}')
                    shutil.copy(os.path.join(foldername, filename), os.path.join(path, filename))
                    show_progress_bar(total, copied)


def close_log(args, logger):
    """
    Close selective_copy.log file and remove it from logger
    file handlers if logging is turned on in command line arguments.
    :param args: Namespace. Command line arguments.
    :param logger: Logger.
    :return: NoneType.
    """
    if args.log:
        logger.handlers[0].close()
        logger.handlers = []
        print('Log saved')


if __name__ == '__main__':
    parser, args = parse_args()
    extension = f'.{args.ext}'
    from_folder = select_source(args)
    total = get_total(from_folder, extension)
    to_folder = select_destination(args)
    logger = create_logger(args, to_folder)
    msg = f'Copying {total} {extension} files from {from_folder} to {to_folder}'
    copied = 0

    # checking for errors
    error = check_for_errors(from_folder, to_folder, extension, total)
    if error:
        logger.error(f'{error}\n')
        close_log(args, logger)
        sys.exit(error)

    # main block
    os.chdir(from_folder)
    if args.preserve:
        print(f'{msg} preserving source folder structure')
        logger.info(f'{msg} preserving source folder structure')
        copy_with_structure(from_folder, to_folder, extension)
    else:
        print(msg)
        logger.info(msg)
        copy(from_folder, to_folder, extension)
    logger.info(f'Process finished\n')
    close_log(args, logger)
