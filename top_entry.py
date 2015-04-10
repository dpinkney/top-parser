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
    LOAD_1_MINUTE = "1 minute load"              # float
    LOAD_5_MINUTES = "5 minute load"               # float
    LOAD_15_MINUTES = "15 minute load"             # float

    # Regular Expressions
    # Uptime has variable time unit output, might be days, minutes, or just hours:min
    RE_UPTIME = re.compile('top - ([\d:]+) up\s+(\d+ days?, \d+:\d+|\d+ mins?|\d+:\d+),\s+(\d+) users?,\s+load average: ([\d.]+), ([\d.]+), ([\d.]+)')
    RE_UPTIME_DAYS = re.compile('(\d+)\s+days?,\s+(\d+):(\d+)')
    RE_UPTIME_HOUR = re.compile('(\d+):(\d+)')
    RE_UPTIME_MIN = re.compile('(\d+)\s+mins?')

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
        Parse uptime state out of a string.  The string format can be one of:
        top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05
        top - 10:53:52 up 2 min,  1 user,  load average: 0.21, 0.16, 0.06
        top - 11:51:42 up  1:00,  1 user,  load average: 0.00, 0.01, 0.05
        """
        logger.debug("Parsing uptime from '{0}'".format(line))
        match = self.RE_UPTIME.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))

        self.header[self.TIME_OF_DAY] = groups[0]
        self.header[self.UPTIME_MINUTES] = self.parseUptimeMinutes(groups[1])
        self.header[self.NUM_USERS] = int(groups[2])
        self.header[self.LOAD_1_MINUTE] = float(groups[3])
        self.header[self.LOAD_5_MINUTES] = float(groups[4])
        self.header[self.LOAD_15_MINUTES] = float(groups[5])

    def parseUptimeMinutes(self, uptimeStr):
        """
        Parse the uptime minutes.  Uptime unit may vary from seconds to minutes, hour and days.
        Example:
        '27 days, 16:32'
        '1:00'
        '2 min'
        """
        match = self.RE_UPTIME_DAYS.match(uptimeStr)
        if match:
            groups = match.groups()
            logger.debug("Parsed groups: {0}".format(groups))
            minutes = int(groups[0]) * 24 * 60 + int(groups[1]) * 60 + int(groups[2])
        else:
            match = self.RE_UPTIME_HOUR.match(uptimeStr)
            if match:
                groups = match.groups()
                logger.debug("Parsed groups: {0}".format(groups))
                minutes = int(groups[0]) * 60 + int(groups[1])
            else:
                match = self.RE_UPTIME_MIN.match(uptimeStr)
                groups = match.groups()
                logger.debug("Parsed groups: {0}".format(groups))
                minutes = int(groups[0])

        logger.debug("Parsed minutes of {0} from {1}".format(minutes, uptimeStr))
        return minutes





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
