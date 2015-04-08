import logging
import re

__author__ = 'Dave Pinkney'

logger = logging.getLogger(__name__)

class TopEntry(object):
    """
    This class represents the output from one iteration of top.
    It will read top output from a file and initialize itself from it.
    """

    # Header Field Names
    TIME_OF_DAY = "timeOfDay"                      # string
    UPTIME_MINUTES = "uptimeMinutes"               # int
    NUM_USERS = "numUsers"                         # int
    LOAD_ONE_MINUTE = "1 minute load"              # float
    LOAD_5_MINUTES = "5 minute load"               # float
    LOAD_15_MINUTES = "15 minute load"             # float

    # Regular Expressions
    RE_UPTIME = re.compile("top - ([\d:]+) up (\d+) days, (\d+):(\d+), (\d+) users,\s+load average: ([\d.]+), ([\d.]+), ([\d.]+)")

    def __init__(self):
        """
        """
        self.header = {}
        self.jobs = {}

    def __str__(self):
        """Convert to string, for str()."""
        return "Header = {0}, Jobs = {1}".format(self.header, self.jobs)

    def parse(self, f):
        """
        Reads a top entry from f and initializes this object from it.
        :throws: Exception if at EOF
        """
        self.parseHeader(f)
        self.parseBody(f)
        logger.debug("Parsed entry: {0}".format(self))

    def parseHeader(self, f):
        """
        :type f - File of top output, next line should be the header, e.g.:

        top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05
        Tasks: 285 total,   1 running, 284 sleeping,   0 stopped,   0 zombie
        %Cpu(s):  2.4 us,  0.5 sy,  0.0 ni, 96.8 id,  0.1 wa,  0.1 hi,  0.0 si,  0.0 st
        KiB Mem:  16355800 total, 15649032 used,   706768 free,   294280 buffers
        KiB Swap:  4095996 total,    96600 used,  3999396 free, 10201704 cached

        :return: a TopEntry instance
        :throws: Exception if at EOF
        """
        self.parseUptime(self.readline(f))
        self.parseTasks(self.readline(f))
        self.parseCpu(self.readline(f))
        self.parseMem(self.readline(f))
        self.parseSwap(self.readline(f))

    def parseUptime(self, line):
        """
        Parse uptime state out of a String with the following format:
        top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05
        """
        logger.debug("Parsing uptime from '{0}'".format(line))
        match = self.RE_UPTIME.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))

        self.header[self.TIME_OF_DAY] = groups[0]
        self.header[self.UPTIME_MINUTES] = int(groups[1]) * (24 * 60) + int(groups[2]) * 60 + int(groups[3])
        self.header[self.NUM_USERS] = int(groups[4])
        self.header[self.LOAD_ONE_MINUTE] = float(groups[5])
        self.header[self.LOAD_5_MINUTES] = float(groups[6])
        self.header[self.LOAD_15_MINUTES] = float(groups[7])

    def parseTasks(self, line):
        pass

    def parseCpu(self, line):
        pass

    def parseMem(self, line):
        pass

    def parseSwap(self, line):
        pass

    def parseBody(self, f):
        """
        :type f - File of top output
        :return: a TopEntry instance
        """
        pass

    def readline(self, f):
        """
        :type f - File to read from
        :throws: Exception if at EOF
        :return: String - the line that was read
        """
        line = f.readline()
        if line:
            return line
        else:
            raise Exception("Encountered unexpected EOF - discarding incomplete entry.")


class Job:
    def __init__(self):
        self.data = {}

    def parseJob(self, f):
        pass

