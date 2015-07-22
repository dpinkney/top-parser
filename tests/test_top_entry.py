import logging
import sys
import unittest

sys.path.append('../')

from top_entry import TopEntry

class TopEntryTestCase(unittest.TestCase):
    """ Tests for TopEntry. """

    def testParseUptime(self):
        """ Tests the parseUptime method. """

        # Typical output
        line = 'top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 1.23, 0.14, 9.05'
        self.checkParseUptime(line, '05:58:39', (27 * 24 * 60 + 16 * 60 + 32), 17, 1.23, 0.14, 9.05)

        # Just rebooted
        line = 'top - 10:53:52 up 2 min,  1 user,  load average: 0.21, 0.16, 0.06'
        self.checkParseUptime(line, '10:53:52', 2, 1, 0.21, 0.16, 0.06)

        # Just rebooted
        line = 'top - 10:53:52 up 2 min,  1 user,  load average: 0.21, 0.16, 0.06'
        self.checkParseUptime(line, '10:53:52', 2, 1, 0.21, 0.16, 0.06)

        # Up 1 hour
        line = 'top - 11:51:42 up  1:00,  1 user,  load average: 0.00, 0.01, 0.05'
        self.checkParseUptime(line, '11:51:42', 60, 1, 0.00, 0.01, 0.05)

        # Up only 1 day
        line = 'top - 10:54:38 up 1 day, 23:29,  1 user,  load average: 0.00, 0.01, 0.05'
        self.checkParseUptime(line, '10:54:38', (1 * 24 * 60 + 23 * 60 + 29), 1, 0.00, 0.01, 0.05)

        # 0 users
        line = 'top - 11:00:26 up 9 min,  0 users,  load average: 0.01, 0.05, 0.05'
        self.checkParseUptime(line, '11:00:26', 9, 0, 0.01, 0.05, 0.05)


    def checkParseUptime(self, line, timeOfDay, uptimeMinutes, numUsers, load1Min, load5Min, load15Min):
        """
        Parse uptime from the provided line, and verify that it parses
        the expected values that were provided.
        """
        entry = TopEntry()
        entry.parseUptime(line)

        self.assertEqual(timeOfDay, entry.header[TopEntry.TIME_OF_DAY])
        self.assertEqual(uptimeMinutes, entry.header[TopEntry.UPTIME_MINUTES])
        self.assertEqual(numUsers, entry.header[TopEntry.NUM_USERS])
        self.assertEqual(load1Min, entry.header[TopEntry.LOAD_1_MINUTE])
        self.assertEqual(load5Min, entry.header[TopEntry.LOAD_5_MINUTES])
        self.assertEqual(load15Min, entry.header[TopEntry.LOAD_15_MINUTES])

    def testParseTasks(self):
        """ Tests the parseTasks method. """

        # Typical output
        line = 'Tasks: 285 total,   1 running, 284 sleeping,   0 stopped,   0 zombie'
        self.checkParseTasks(line, 285, 1, 284, 0, 0)

        line = 'Tasks: 0 total,   0 running, 0 sleeping,   0 stopped,   0 zombie'
        self.checkParseTasks(line, 0, 0, 0, 0, 0)

        line = 'Tasks: 123 total,   456 running, 789 sleeping,   321 stopped,   654 zombie'
        self.checkParseTasks(line, 123, 456, 789, 321, 654)

    def checkParseTasks(self, line, numTotal, numRunning, numSleeping, numStopped, numZombie):
        """
        Parse task info from the provided line, and verify that it parses
        the expected values that were provided.
        """
        entry = TopEntry()
        entry.parseTasks(line)

        self.assertEqual(numTotal, entry.header[TopEntry.TASKS_TOTAL])
        self.assertEqual(numRunning, entry.header[TopEntry.TASKS_RUNNING])
        self.assertEqual(numSleeping, entry.header[TopEntry.TASKS_SLEEPING])
        self.assertEqual(numStopped, entry.header[TopEntry.TASKS_STOPPED])
        self.assertEqual(numZombie, entry.header[TopEntry.TASKS_ZOMBIE])


    def testParseCpu(self):
        """ Tests the parseCpu method. """

        # Typical output
        line = '%Cpu(s):  2.4 us,  0.5 sy,  0.0 ni, 96.8 id,  0.1 wa,  0.1 hi,  0.0 si,  0.0 st'
        self.checkParseCpu(line, 2.4, 0.5, 0.0, 96.8, 0.1, 0.1, 0.0, 0.0)

        line = '%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni, 0.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st'
        self.checkParseCpu(line, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        line = '%Cpu(s):  100.1 us,  99.9 sy,  90.0 ni, 110.123 id,  111.222 wa,  333.444 hi,  100.100 si,  200.200 st'
        self.checkParseCpu(line, 100.1, 99.9, 90.0, 110.123, 111.222, 333.444, 100.100, 200.200)

        line = 'Cpu(s):  2.1%us,  1.0%sy,  0.0%ni, 85.4%id, 11.5%wa,  0.0%hi,  0.1%si,  0.0%st'
        self.checkParseCpu(line, 2.1, 1.0, 0.0, 85.4, 11.5, 0.0, 0.1, 0.0)

    def checkParseCpu(self, line, unniced, system, niced, idle, wait, hi, si, st):
        """
        Parse cpu info from the provided line, and verify that it parses
        the expected values that were provided.
        """
        entry = TopEntry()
        entry.parseCpu(line)

        self.assertEqual(unniced, entry.header[TopEntry.CPU_UNNICED])
        self.assertEqual(system, entry.header[TopEntry.CPU_SYSTEM])
        self.assertEqual(niced, entry.header[TopEntry.CPU_NICED])
        self.assertEqual(idle, entry.header[TopEntry.CPU_IDLE])
        self.assertEqual(wait, entry.header[TopEntry.CPU_WAIT])
        self.assertEqual(hi, entry.header[TopEntry.CPU_HI])
        self.assertEqual(si, entry.header[TopEntry.CPU_SI])
        self.assertEqual(st, entry.header[TopEntry.CPU_ST])

    def testParseMem(self):
        """ Tests the parseMem method. """

        # Typical output
        line = 'KiB Mem:  16355800 total, 15649032 used,   706768 free,   294280 buffers'
        self.checkParseMem(line, 16355800, 15649032, 706768, 294280)

        line = 'KiB Mem:  0 total, 0 used,   0 free,   1 buffer'
        self.checkParseMem(line, 0, 0, 0, 1)

        line = 'KiB Mem:  100 total, 200 used,   300 free,   400 buffers'
        self.checkParseMem(line, 100, 200, 300, 400)

        line = 'Mem:   8170096k total,  7148836k used,  1021260k free,   337592k buffers'
        self.checkParseMem(line, 8170096, 7148836, 1021260, 337592)

    def checkParseMem(self, line, total, used, free, buffers):
        """
        Parse mem info from the provided line, and verify that it parses
        the expected values that were provided.
        """
        entry = TopEntry()
        entry.parseMem(line)

        self.assertEqual(total, entry.header[TopEntry.MEM_TOTAL])
        self.assertEqual(used, entry.header[TopEntry.MEM_USED])
        self.assertEqual(free, entry.header[TopEntry.MEM_FREE])
        self.assertEqual(buffers, entry.header[TopEntry.MEM_BUFFERS])

    def testParseSwap(self):
        """ Tests the parseSwap method. """

        # Typical output
        line = 'KiB Swap:  4095996 total,    96600 used,  3999396 free, 10201704 cached'
        self.checkParseSwap(line, 4095996, 96600, 3999396, 10201704)

        line = 'KiB Swap:  0 total, 0 used,   0 free,   1 cached'
        self.checkParseSwap(line, 0, 0, 0, 1)

        line = 'KiB Swap:  100 total, 200 used,   300 free,   400 cached'
        self.checkParseSwap(line, 100, 200, 300, 400)

        line = 'Swap:  3146748k total,   905060k used,  2241688k free,  1705700k cached'
        self.checkParseSwap(line, 3146748, 905060, 2241688, 1705700)

    def checkParseSwap(self, line, total, used, free, buffers):
        """
        Parse swap info from the provided line, and verify that it parses
        the expected values that were provided.
        """
        entry = TopEntry()
        entry.parseSwap(line)

        self.assertEqual(total, entry.header[TopEntry.SWAP_TOTAL])
        self.assertEqual(used, entry.header[TopEntry.SWAP_USED])
        self.assertEqual(free, entry.header[TopEntry.SWAP_FREE])
        self.assertEqual(buffers, entry.header[TopEntry.SWAP_CACHED])


if __name__ == '__main__':
    logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel)

    unittest.main()
