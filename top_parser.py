#!/usr/bin/python
"""
This module will parse a set of output that has been generated by top in batch mode.
It expects to be fed the output corresponding to one iteration of top.
"""

import argparse
import logging
import os
import sys

from top_entry import TopEntry

__author__ = 'Dave Pinkney'

logger = logging.getLogger(__name__)

class TopParser(object):

    def __init__(self, fileName):
        """
        """
        self.fileName = fileName
        self.entries = []

    def parse(self):
        logger.debug("Parsing file {0}".format(self.fileName))

        # Parse the file
        # Pass output sequence from top to TopParser
        with open(self.fileName, 'r') as f:
            while True:
                firstLine = f.readline()
                if not firstLine:
                    break
                topEntry = TopEntry().parse(firstLine, f)
                self.entries.append(topEntry)

                
        logger.info("Parsed {0} entries from {1}".format(len(self.entries), self.fileName))



def main(argv):
    examples = """
    Examples:
    # Parse top data from the specified output file, generated via "top -b":
        %prog topOutput.log

    # Parse top data from an output file containing timestamps, generated with a script run via cron such as:
    #
    #  date "+%m/%d %H:%M:%S" >> topWithDate.log
    #  top -b -n1 -H >> topWithDate.log
        %prog topWithDate.log

    """
    parser = argparse.ArgumentParser(description="""This tool is used to parse output from the top command""",
                                     epilog=examples, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fileName", type=str, default=None, help="File to parse")
    parser.add_argument("-v", "--verbose", action='store_true', help="True to enable verbose logging mode")
    options = parser.parse_args(argv)

    if options.verbose:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO

    logging.basicConfig(level=logLevel)

    logger.debug("Got options: {0}".format(options))

    topParser = TopParser(options.fileName)
    topParser.parse()


if __name__ == "__main__":
    main(sys.argv[1:])
