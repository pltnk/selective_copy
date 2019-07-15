# slcp.py - command line application that copies all files with given extensions
# from a directory and its subfolders to another directory.
# Allows to preserve a source folder structure, to process only files without given extensions,
# to move files instead of copying, to exclude certain files from processing and to create a log if necessary.
# Opens a filedialog if source and/or destination are not given in the command line.
# Creates folders in destination if they don't exist.
# This project is licensed under the MIT License.
# Copyright (c) 2019 Kirill Plotnikov


import logging
import os
import shutil
import sys
from argparse import ArgumentParser
from tkinter.filedialog import askdirectory


def parse_args():
    """
    Parse command line arguments, format given extensions and arguments containing paths.
    :return: tuple of (ArgumentParser, Namespace). Parser itself and all arguments.
    """
    parser = ArgumentParser(usage='slcp ext [ext ...] [-s SRC] [-d DST] [-sc | -dc] '
                                  '[-p] [-i] [-m] [-e FILE [FILE ...]] [-l] [-h]',
                            description='Copy all files with given extensions from a directory and its subfolders '
                                        'to another directory. '
                                        'A destination folder must be outside of a source folder.')
    parser.add_argument('ext', nargs='+', help='one or more extensions, enter without a dot, separate by spaces')
    parser.add_argument('-s', '--source', help='source folder path', metavar='SRC')
    parser.add_argument('-d', '--dest', help='destination folder path', metavar='DST')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-sc', '--srccwd', action='store_true', help='use current working directory as a source')
    group.add_argument('-dc', '--dstcwd', action='store_true', help='use current working directory as a destination')
    parser.add_argument('-p', '--preserve', action='store_true', help='preserve source folder structure')
    parser.add_argument('-i', '--invert', action='store_true', help='process only files without given extensions')
    parser.add_argument('-m', '--move', action='store_true', help='move files instead of copying')
    parser.add_argument('-e', '--exclude', nargs='+', help='exclude certain files from processing', metavar='FILE')
    parser.add_argument('-l', '--log', action='store_true', help='create and save log to the destination folder')
    args = parser.parse_args()
    args.ext = tuple(set(f'.{item}' for item in args.ext))
    if args.source:
        args.source = os.path.normpath(args.source.strip())
    if args.dest:
        args.dest = os.path.normpath(args.dest.strip())
    args.exclude = tuple(set(args.exclude)) if args.exclude else tuple()
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
    logger.setLevel(logging.CRITICAL)
    if args.log:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.path.join(destination, 'selective_copy.log'), encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(message)s', '%d.%m.%Y %H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


def check_for_errors(source, destination, extensions, total):
    """
    Check for errors, raise corresponding
    Exception if any errors occurred.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param extensions: tuple of str. Extensions of files.
    :param total: int. Number of files with extensions in source folder.
    :return: str or NoneType. Error statement or None.
    """
    if not os.path.exists(source):
        raise Exception(f'Error: Source path {source} does not exist.')
    elif total == 0:
        raise Exception(f'Error: There are no {", ".join(extensions)} files in {source}.')
    elif source in destination:
        raise Exception(f'Error: A destination folder must be outside of source folder. '
                        f'Paths given: source - {source} | destination - {destination}.')
    else:
        pass


def select_source(args):
    """
    Check if the source path is in the command line arguments,
    if not ask user for input using filedialog.
    :param args: Namespace. Command line arguments.
    :return: str. Source folder path.
    """
    if args.srccwd:
        source = os.getcwd()
    else:
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
    if args.dstcwd:
        destination = os.getcwd()
    else:
        if args.dest is None:
            print('Choose a destination path.')
            destination = os.path.normpath(askdirectory())
            print(f'Destination path: {destination}')
        else:
            destination = args.dest
            if not os.path.exists(destination):
                os.makedirs(destination)
    return destination


def get_todo(source, destination, args):
    """
    Create a to-do list where each sublist represents one file and contains
    source and destination paths for this file.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param args: Namespace. Command line arguments.
    :return: list of list of str. To-do list.
    """
    todo_list = []
    try:
        os.chdir(source)
        for foldername, _, filenames in os.walk(source):
            if args.preserve:
                path = os.path.join(destination,
                                    f'{"not_" if args.invert else ""}{"_".join(args.ext)}_{os.path.basename(source)}',
                                    os.path.relpath(foldername))
            for filename in filenames:
                if (filename.endswith(args.ext) ^ args.invert) and filename not in args.exclude:
                    if args.preserve:
                        todo_list.append([os.path.join(foldername, filename), os.path.join(path, filename)])
                    else:
                        todo_list.append([os.path.join(foldername, filename), os.path.join(destination, filename)])
    except FileNotFoundError:
        pass
    return todo_list


def show_progress_bar(total, counter=0):
    """
    Print progress bar.
    :param total: int. Total number of iterations.
    :param counter: int. Current iteration.
    :return: NoneType.
    """
    global processed
    try:
        term_width = os.get_terminal_size(0)[0]
    except OSError:
        term_width = 80
    length = term_width - (len(str(total)) + 30)
    percent = round(100 * (counter / total))
    filled = int(length * counter // total)
    bar = f'|{"=" * filled}{"-" * (length - filled)}|' if term_width > 50 else ''
    suffix = f'Files left: {total - counter} ' if counter < total else 'Done           '
    print(f'\rProgress: {bar} {percent}% {suffix}', end='\r', flush=True)
    processed += 1
    if counter == total:
        print()


def process(todo_list, action):
    """
    Copy or move files according to source and destination paths
    given in todo_list. Each item in this list represents one file.
    item[0] - source, item[1] - destination.
    :param todo_list: list of list of str.
    :param action: must be either shutil.copy or shutil.move
    :return: NoneType.
    """
    show_progress_bar(total)
    for item in todo_list:
        if not os.path.exists(os.path.dirname(item[1])):
            os.makedirs(os.path.dirname(item[1]))
        try:
            if not os.path.exists(item[1]):
                logger.info(f'{item[0]}')
                action(item[0], item[1])
            else:
                new_filename = f'{os.path.basename(os.path.dirname(item[0]))}_{os.path.basename(item[1])}'
                logger.info(f'*{item[0]} saving it as {new_filename}')
                action(item[0], os.path.join(os.path.dirname(item[1]), new_filename))
        except Exception as e:
            logger.error(f'*Unable to process {item[0]}, an error occurred: {e}')
        show_progress_bar(total, processed)


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


def main():
    """
    Check for errors and terminate the program if found any.
    If errors are absent process files according to the
    command line arguments.
    :return: NoneType.
    """
    # checking for errors
    try:
        check_for_errors(from_folder, to_folder, args.ext, total)
    except Exception as e:
        logger.error(f'{e}\n')
        close_log(args, logger)
        sys.exit(e)

    # main block
    print(message)
    logger.info(message)
    process(to_process, action)
    logger.info(f'Process finished\n')
    close_log(args, logger)


parser, args = parse_args()
from_folder = select_source(args)
to_folder = select_destination(args)
logger = create_logger(args, to_folder)
to_process = get_todo(from_folder, to_folder, args)
total = len(to_process)
action = shutil.move if args.move else shutil.copy
excluded = ', '.join(args.exclude)
processed = 0
message = f'{"Moving" if args.move else "Copying"} ' \
          f'{total} file{"s" if total > 1 else ""} ' \
          f'{"without" if args.invert else "with"} ' \
          f'{", ".join(args.ext)} extension{"s" if len(args.ext) > 1 else ""} ' \
          f'from {from_folder} to {to_folder} ' \
          f'{"preserving source folder structure" if args.preserve else ""}' \
          f'{f", excluding {excluded}" if len(args.exclude) > 0 else ""}'


if __name__ == '__main__':
    main()

