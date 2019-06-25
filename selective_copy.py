# slcp.py - copies all files with given extension from a directory
# and its subfolders to another directory.
# Allows to preserve source folder structure and to create a log if necessary.
# Opens a filedialog if source and/or destination are not given in the command line.
# Creates folders in destination if they don't exist.
# This project is licensed under the MIT License.
# Copyright (c) 2019 Kirill Plotnikov


import logging, os, shutil, sys
from argparse import ArgumentParser
from tkinter.filedialog import askdirectory


def parse_args():
    """
    Parse command line arguments and format arguments containing paths.
    :return: tuple of (ArgumentParser, Namespace). Parser itself and all arguments.
    """
    parser = ArgumentParser(usage='slcp ext [-s SRC] [-d DST] [-sc | -dc] [-p] [-l] [-h]',
                            description='Copy all files with given extension from a directory and its subfolders '
                                        'to another directory. '
                                        'A destination folder must be outside of a source folder.')
    parser.add_argument('ext', help='extension of the files to copy, enter without a dot', type=str)
    parser.add_argument('-s', '--source', help='source folder path', type=str, metavar='SRC')
    parser.add_argument('-d', '--dest', help='destination folder path', type=str, metavar='DST')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-sc', '--srccwd', action='store_true', help='use current working directory as a source')
    group.add_argument('-dc', '--dstcwd', action='store_true', help='use current working directory as a destination')
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
    logger.setLevel(logging.CRITICAL)
    if args.log:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.path.join(destination, 'selective_copy.log'), encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(message)s', '%d.%m.%Y %H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


def check_for_errors(source, destination, extension, total):
    """
    Check for errors, raise corresponding
    Exception if any errors occurred.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param extension: str. Extension of files.
    :param total: int. Number of files with extension in source folder.
    :return: str or NoneType. Error statement or None.
    """
    if not os.path.exists(source):
        raise Exception(f'Error: Source path {source} does not exist.')
    elif total == 0:
        raise Exception(f'Error: There are no {extension} files in {source}.')
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


def get_todo(source, destination, extension, args):
    """
    Create a to-do list where each sublist represents one file and contains
    source and destination paths for this file.
    :param source: str. Source folder path.
    :param destination: str. Destination folder path.
    :param extension: str. Extension of the files to copy.
    :param args: Namespace. Command line arguments.
    :return: list of list of str. To-do list.
    """
    todo_list = []
    try:
        os.chdir(source)
        for foldername, subfolders, filenames in os.walk(source):
            if args.preserve:
                path = os.path.join(destination, f'{extension}_{os.path.basename(source)}', os.path.relpath(foldername))
            for filename in filenames:
                if filename.endswith(extension):
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
    global copied
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
    copied += 1
    if counter == total:
        print()


def copy(todo_list):
    """
    Copy files according to source and destination paths
    given in todo_list. Each item in this list represents one file.
    item[0] - source, item[1] - destination.
    :param todo_list: list of list of str.
    :return: NoneType.
    """
    show_progress_bar(total)
    for item in todo_list:
        if not os.path.exists(os.path.dirname(item[1])):
            os.makedirs(os.path.dirname(item[1]))
        if not os.path.exists(item[1]):
            logger.info(f'{item[0]}')
            shutil.copy(item[0], item[1])
        else:
            new_filename = f'{os.path.basename(os.path.dirname(item[0]))}_{os.path.basename(item[1])}'
            logger.info(f'*{item[0]} saving it as {new_filename}')
            shutil.copy(item[0], os.path.join(os.path.dirname(item[1]), new_filename))
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


def main():
    """
    Check for errors and terminate the program if found any.
    If errors are absent copy files according to the
    command line arguments.
    :return: NoneType.
    """
    # checking for errors
    try:
        check_for_errors(from_folder, to_folder, extension, total)
    except Exception as e:
        logger.error(f'{e}\n')
        close_log(args, logger)
        sys.exit(e)

    # main block
    if args.preserve:
        print(f'{msg} preserving source folder structure')
        logger.info(f'{msg} preserving source folder structure')
    else:
        print(msg)
        logger.info(msg)
    copy(to_copy)
    logger.info(f'Process finished\n')
    close_log(args, logger)


parser, args = parse_args()
extension = f'.{args.ext}'
from_folder = select_source(args)
to_folder = select_destination(args)
logger = create_logger(args, to_folder)
to_copy = get_todo(from_folder, to_folder, extension, args)
total = len(to_copy)
msg = f'Copying {total} {extension} files from {from_folder} to {to_folder}'
copied = 0


if __name__ == '__main__':
    main()
