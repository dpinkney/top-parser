import logging
import re

__author__ = 'Dave Pinkney'

logger = logging.getLogger(__name__)

class Job(object):

    JOB_PID = 'pid'                  # string
    JOB_USER = 'user'                # string
    JOB_PR = 'priority'              # string
    JOB_NI = 'nice'                  # int
    JOB_VIRT = 'memVirtual'          # int   in KiB
    JOB_RES = 'memResident'          # int   in KiB
    JOB_SHR = 'memShared'            # int   in KiB
    JOB_STATUS = 'status'            # string
    JOB_CPU = 'cpuPercent'           # float
    JOB_MEM = 'memPercent'           # float
    JOB_TIME = 'cpuTotalTime'        # string
    JOB_COMMAND = 'command'          # string

    RE_JOB = re.compile("""^\s*(\d+)                 # PID
                            \s+(\w+)                 # user
                            \s+([-\w]+)              # priority
                            \s+([-\d]+)              # nice
                            \s+(\d+|\d+[.\d]+\w?)    # memVirtual
                            \s+(\d+|\d+[.\d]+\w?)    # memResident
                            \s+(\d+|\d+[.\d]+\w?)    # memShared
                            \s+(\w+)                 # status
                            \s+([\d.]+)              # cpuPercent
                            \s+([\d.]+)              # memPercent
                            \s+(\d+:\d+[.\d]*)       # cpuTotalTime
                            \s+(.+)                  # command
                            $""", re.VERBOSE)

    RE_JOB_RES = re.compile('^(\d+)$')
    RE_JOB_RES_SCALED = re.compile('^(\d+[.\d]*)([a-z])$')

    def __init__(self):
        """
        """
        self.info = {}

    def __str__(self):
        """Convert to string, for str()."""
        return "Job({0})".format(self.info)

    def getPid(self):
        """Returns the pid for this job"""
        return self.info[self.JOB_PID]

    def parse(self, line):
        """
        Parse this job's state from a line of top output
        Sample input:
        '  662 root      20   0  273524  86820  17340 S   6.2  0.5 338:15.30 Xorg'
        '32469 dpinkney  20   0 3920412 2.403g  72804 S   6.2 15.4   2709:11 firefox'
        """
        logger.debug("Parsing job '{0}'".format(line))
        match = self.RE_JOB.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))

        self.info[self.JOB_PID] = groups[0]
        self.info[self.JOB_USER] = groups[1]
        self.info[self.JOB_PR] = groups[2]
        self.info[self.JOB_NI] = int(groups[3])
        self.info[self.JOB_VIRT] = self.parseScaledMem(groups[4])
        self.info[self.JOB_RES] = self.parseScaledMem(groups[5])
        self.info[self.JOB_SHR] = self.parseScaledMem(groups[6])
        self.info[self.JOB_STATUS] = groups[7]
        self.info[self.JOB_CPU] = float(groups[8])
        self.info[self.JOB_MEM] = float(groups[9])
        self.info[self.JOB_TIME] = groups[10]
        self.info[self.JOB_COMMAND] = groups[11]


    def parseScaledMem(self, resStr):
        """
        The memory values may contain a postfix, in which case we should convert it from mb or gb to kb
        :return: The memory value in KiB
        """
        logger.debug("Parsing res from {0}".format(resStr))

        match = self.RE_JOB_RES.match(resStr)
        if match:
            return int(match.groups()[0])
        else:
            match = self.RE_JOB_RES_SCALED.match(resStr)
            if match:
                groups = match.groups()
                value = float(groups[0])

                if groups[1] == 'm':
                    return int(value * 1024)
                elif groups[1] == 'g':
                    return int(value * 1024 * 1024)
                else:
                    raise Exception ("Unknown value in {0}".format(resStr))
            else:
                raise Exception ("Unknown value in {0}".format(resStr))
