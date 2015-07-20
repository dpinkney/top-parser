import datetime
import logging
import re

from job import Job

__author__ = 'Dave Pinkney'

logger = logging.getLogger(__name__)

class TopEntry(object):
    """
    This class represents the output from one iteration of top.
    It will read top output from a file and initialize itself from it.
    """
    YEAR = datetime.date.today().year

    HAS_DATE_INFO = None                          # tracks whether the top input has a date header

    # Define Regular Expressions and Header Field Names

    # Date / Timestamp header - Not part of standard top output
    DATE = 'date'                                  # datetime.date
    RE_DATE = re.compile('^(\d+)/(\d+)')

    # Uptime
    TIME_OF_DAY = 'timeOfDay'                      # string
    UPTIME_MINUTES = 'uptimeMinutes'               # int
    NUM_USERS = 'numUsers'                         # int
    LOAD_1_MINUTE = '1 minute load'                # float
    LOAD_5_MINUTES = '5 minute load'               # float
    LOAD_15_MINUTES = '15 minute load'             # float
    # Uptime has variable time unit output, might be days, minutes, or just hours:min

    RE_UPTIME = re.compile("""^top\s+-
                              \s+(\d+):(\d+):(\d+)                                 # time of day
                              \s+up
                              \s+(\d+\s+days?,\s+\d+:\d+                           # uptime
                                  |\d+\s+days?,\s+\d+\s+mins?                      # uptime
                                  |\d+\s+mins?                                     # uptime
                                  |\d+:\d+),                                       # uptime
                              \s+(\d+)\s+users?,                                   # num users
                              \s+load\s+average:
                              \s+([\d.]+),\s+([\d.]+),\s+([\d.]+)                  # load
                              """, re.VERBOSE)

    RE_UPTIME_DAYS = re.compile('(\d+)\s+days?,\s+(\d+):(\d+)')
    RE_UPTIME_DAYS_MIN = re.compile('(\d+)\s+days?,\s+(\d+)\s+mins?')
    RE_UPTIME_HOUR = re.compile('(\d+):(\d+)')
    RE_UPTIME_MIN = re.compile('(\d+)\s+mins?')

    # Tasks
    TASKS_TOTAL = 'tasksTotal'                     # int
    TASKS_RUNNING = 'tasksRunning'                 # int
    TASKS_SLEEPING = 'tasksSleeping'               # int
    TASKS_STOPPED = 'tasksStopped'                 # int
    TASKS_ZOMBIE = 'tasksZombie'                   # int
    RE_TASKS = re.compile('^Tasks:\s+(\d+) total,\s+(\d+)\s+running,\s+(\d+)\s+sleeping,\s+(\d+)\s+stopped,\s+(\d+)\s+zombie')

    # CPU
    CPU_UNNICED = 'cpuUnNiced'                     # float
    CPU_SYSTEM = 'cpuSystem'                       # float
    CPU_NICED = 'cpuNiced'                         # float
    CPU_IDLE = 'cpuIdle'                           # float
    CPU_WAIT = 'cpuIoWait'                         # float
    CPU_HI = 'cpuHardwareInt'                      # float
    CPU_SI = 'cpuSoftwareInt'                      # float
    CPU_ST = 'cpuStolen'                           # float
    RE_CPU = re.compile('^%Cpu\(s\):\s+([\d.]+) us,\s+([\d.]+) sy,\s+([\d.]+) ni,\s+([\d.]+) id,\s+([\d.]+) wa,\s+([\d.]+) hi,\s+([\d.]+) si,\s+([\d.]+) st')

    # Memory
    MEM_TOTAL = 'memTotal'
    MEM_USED = 'memUsed'
    MEM_FREE = 'memFree'
    MEM_BUFFERS = 'memBuffers'
    RE_MEM = re.compile('^KiB Mem:\s+(\d+) total,\s+(\d+) used,\s+(\d+) free,\s+(\d+) buffers?')

    # Swap
    SWAP_TOTAL = 'swapTotal'
    SWAP_USED = 'swapUsed'
    SWAP_FREE = 'swapFree'
    SWAP_CACHED = 'swapCached'
    RE_SWAP = re.compile('^KiB Swap:\s+(\d+) total,\s+(\d+) used,\s+(\d+) free,\s+(\d+) cached')

    # Jobs
    RE_JOB_HEADER = re.compile('^\s+PID\s+USER\s+PR\s+NI\s+VIRT\s+RES\s+SHR\s+S\s+%CPU\s+%MEM\s+TIME\+\s+COMMAND')

    def __init__(self):
        """
        """
        self.header = {}
        self.jobs = {}

    def __str__(self):
        """Convert to string, for str()."""
        return "Header = {0}, {1} Jobs ".format(self.header, len(self.jobs))

    def parse(self, firstLine, f):
        """
        Reads a top entry from f and initializes this object from it.
        :type string: The first line of input read from f, it should be the top header
        :type f - File of top output, with one line consumed
        :throws: Exception if at EOF
        """
        self.parseHeader(firstLine, f)
        self.eatBlankLine(f)
        self.parseBody(f)
        logger.debug("Parsed entry: {0}".format(self))

    def parseHeader(self, firstLine, f):
        """
        :type string: The first line of input read from f, it should be the top header
        :type f - File of top output, with one line consumed

        top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05
        Tasks: 285 total,   1 running, 284 sleeping,   0 stopped,   0 zombie
        %Cpu(s):  2.4 us,  0.5 sy,  0.0 ni, 96.8 id,  0.1 wa,  0.1 hi,  0.0 si,  0.0 st
        KiB Mem:  16355800 total, 15649032 used,   706768 free,   294280 buffers
        KiB Swap:  4095996 total,    96600 used,  3999396 free, 10201704 cached

        or:

        05/27 05:58:39
        top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05
        Tasks: 285 total,   1 running, 284 sleeping,   0 stopped,   0 zombie
        %Cpu(s):  2.4 us,  0.5 sy,  0.0 ni, 96.8 id,  0.1 wa,  0.1 hi,  0.0 si,  0.0 st
        KiB Mem:  16355800 total, 15649032 used,   706768 free,   294280 buffers
        KiB Swap:  4095996 total,    96600 used,  3999396 free, 10201704 cached

        :return: a TopEntry instance
        :throws: Exception if at EOF
        """

        if HAS_DATE_INFO == None or HAS_DATE_INFO:
            firstLine = self.parseDate(f, firstLine)

        self.parseUptime(firstLine)
        self.parseTasks(self.readline(f))
        self.parseCpu(self.readline(f))
        self.parseMem(self.readline(f))
        self.parseSwap(self.readline(f))


    def parseDate(self, f, line):
        """
        Try to parse the DATE from line.  If we find the DATE, store it in this object,
        set HAS_DATE_INFO, and return the next line of input from f
        :return: The next line of text, or line if it did not match DATE
        """
        match = self.RE_DATE.match(line)
        if match:
            groups = match.groups()
            HAS_DATE_INFO = True
            self.header[self.DATE] = datetime.date(YEAR, int(groups[0]), int(groups[1]))
            line = self.readline(f)

        return line

    def parseUptime(self, line):
        """
        Parse uptime state out of a string and update this object's state.
        The string format can be one of:
        top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05
        top - 10:53:52 up 2 min,  1 user,  load average: 0.21, 0.16, 0.06
        top - 11:51:42 up  1:00,  1 user,  load average: 0.00, 0.01, 0.05
        """
        logger.debug("Parsing uptime from '{0}'".format(line))
        match = self.RE_UPTIME.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))

        # Can't recall why I broke this out into components - to plot time as #seconds?
        hours = groups[0]
        minutes = groups[1]
        seconds = groups[2]
        self.header[self.TIME_OF_DAY] = "{0}:{1}:{2}".format(hours, minutes, seconds)

        self.header[self.UPTIME_MINUTES] = self.parseUptimeMinutes(groups[3])
        self.header[self.NUM_USERS] = int(groups[4])
        self.header[self.LOAD_1_MINUTE] = float(groups[5])
        self.header[self.LOAD_5_MINUTES] = float(groups[6])
        self.header[self.LOAD_15_MINUTES] = float(groups[7])

    def parseUptimeMinutes(self, line):
        """
        Parse the uptime minutes and return it.
        The uptime unit varies from seconds to minutes, hour and days.
        Example:
        '27 days, 16:32'
        '1:00'
        '2 min'
        """
        match = self.RE_UPTIME_DAYS.match(line)
        if match:
            groups = match.groups()
            logger.debug("Parsed groups: {0}".format(groups))
            minutes = int(groups[0]) * 24 * 60 + int(groups[1]) * 60 + int(groups[2])
            return minutes

        match = self.RE_UPTIME_DAYS_MIN.match(line)
        if match:
            groups = match.groups()
            logger.debug("Parsed groups: {0}".format(groups))
            minutes = int(groups[0]) * 24 * 60 + int(groups[1])
            return minutes

        match = self.RE_UPTIME_HOUR.match(line)
        if match:
            groups = match.groups()
            logger.debug("Parsed groups: {0}".format(groups))
            minutes = int(groups[0]) * 60 + int(groups[1])
            return minutes

        match = self.RE_UPTIME_MIN.match(line)
        if match:
            groups = match.groups()
            logger.debug("Parsed groups: {0}".format(groups))
            minutes = int(groups[0])
            return minutes


        raise Exception("Could not parse uptime: {0}".format(line))

    def parseTasks(self, line):
        """
        Parse the tasks info from line and update this object's state
        Example input:
        Tasks: 285 total,   1 running, 284 sleeping,   0 stopped,   0 zombie
        """
        logger.debug("Parsing tasks from {0}".format(line))

        match = self.RE_TASKS.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))

        self.header[self.TASKS_TOTAL] = int(groups[0])
        self.header[self.TASKS_RUNNING] = int(groups[1])
        self.header[self.TASKS_SLEEPING] = int(groups[2])
        self.header[self.TASKS_STOPPED] = int(groups[3])
        self.header[self.TASKS_ZOMBIE] = int(groups[4])


    def parseCpu(self, line):
        """
        Parse the cpu information from line and store it in this object's state
        %Cpu(s):  2.4 us,  0.5 sy,  0.0 ni, 96.8 id,  0.1 wa,  0.1 hi,  0.0 si,  0.0 st
        """
        logger.debug("Parsing Cpu from {0}".format(line))

        match = self.RE_CPU.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))
        self.header[self.CPU_UNNICED] = float(groups[0])
        self.header[self.CPU_SYSTEM] = float(groups[1])
        self.header[self.CPU_NICED] = float(groups[2])
        self.header[self.CPU_IDLE] = float(groups[3])
        self.header[self.CPU_WAIT] = float(groups[4])
        self.header[self.CPU_HI] = float(groups[5])
        self.header[self.CPU_SI] = float(groups[6])
        self.header[self.CPU_ST] = float(groups[7])

    def parseMem(self, line):
        """
        Parse the mem information from line and store it in this object's state
        KiB Mem:  16355800 total, 15649032 used,   706768 free,   294280 buffers
        """
        logger.debug("Parsing Mem from {0}".format(line))

        match = self.RE_MEM.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))
        self.header[self.MEM_TOTAL] = int(groups[0])
        self.header[self.MEM_USED] = int(groups[1])
        self.header[self.MEM_FREE] = int(groups[2])
        self.header[self.MEM_BUFFERS] = int(groups[3])

    def parseSwap(self, line):
        """
        Parse the swap information from line and store it in this object's state
        KiB Swap:  4095996 total,    96600 used,  3999396 free, 10201704 cached
        """
        logger.debug("Parsing Swap from {0}".format(line))

        match = self.RE_SWAP.match(line)
        groups = match.groups()
        logger.debug("Got groups: {0}".format(groups))
        self.header[self.SWAP_TOTAL] = int(groups[0])
        self.header[self.SWAP_USED] = int(groups[1])
        self.header[self.SWAP_FREE] = int(groups[2])
        self.header[self.SWAP_CACHED] = int(groups[3])


    def parseBody(self, f):
        """
        :type f - File of top output. Next line should be the header for the jobs section
        :return: a TopEntry instance
        Expected input format:

          PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
         1453 dpinkney  20   0 1983544 409608  44200 S  12.5  2.5 480:36.59 cinnamon
          662 root      20   0  273524  86820  17340 S   6.2  0.5 338:15.30 Xorg
        """
        # strip off the header
        self.readHeader(f)

        while True:
            line = f.readline()
            logger.debug('read line: {0}'.format(line))
            if not line or len(line) == 1:
                break;
            else:
                job = Job()
                job.parse(line)
                logger.debug('read job: {0}'.format(job))
                if self.jobs.has_key(job.getPid()):
                    raise Exception ("Duplicate pid: {0}".format(job.getPid()))
                else:
                    self.jobs[job.getPid()] = job


    def readHeader(self, f):
        """
        Reads the header line from the job section of the top output.
        This just validates that we're at the right point in the file.
        """
        line = self.readline(f)
        match = self.RE_JOB_HEADER.match(line)
        if not match:
            raise Exception("Did not parse header correctly: '{0}'".format(line))


    def eatBlankLine(self, f):
        """
        Read a line from f and verify that is it empty.
        Throws an exception if the line has content.
        """
        line = self.readline(f).strip()
        if line:
            raise Exception("Expected blank line, but got: '{0}'".format(line))

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
