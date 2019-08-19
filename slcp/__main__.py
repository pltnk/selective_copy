"""
This module is a part of slcp command line application
and is licensed under the MIT License.
Copyright (c) 2019 Kirill Plotnikov
GitHub: https://github.com/pltnk/selective_copy
PyPi: https://pypi.org/project/slcp/
"""


from slcp.cli import ArgParser
from slcp.process import Handler


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
