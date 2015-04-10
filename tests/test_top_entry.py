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
        uptimeLine = 'top - 05:58:39 up 27 days, 16:32, 17 users,  load average: 0.01, 0.04, 0.05'
        self.checkParseUptime(uptimeLine, '05:58:39', (27 * 24 * 60 + 16 * 60 + 32), 17, 0.01, 0.04, 0.05)

        # Just rebooted
        uptimeLine = 'top - 10:53:52 up 2 min,  1 user,  load average: 0.21, 0.16, 0.06'
        self.checkParseUptime(uptimeLine, '10:53:52', 2, 1, 0.21, 0.16, 0.06)

        # Just rebooted
        uptimeLine = 'top - 10:53:52 up 2 min,  1 user,  load average: 0.21, 0.16, 0.06'
        self.checkParseUptime(uptimeLine, '10:53:52', 2, 1, 0.21, 0.16, 0.06)

        # Up 1 hour
        uptimeLine = 'top - 11:51:42 up  1:00,  1 user,  load average: 0.00, 0.01, 0.05'
        self.checkParseUptime(uptimeLine, '11:51:42', 60, 1, 0.00, 0.01, 0.05)

        # Up only 1 day
        uptimeLine = 'top - 10:54:38 up 1 day, 23:29,  1 user,  load average: 0.00, 0.01, 0.05'
        self.checkParseUptime(uptimeLine, '10:54:38', (1 * 24 * 60 + 23 * 60 + 29), 1, 0.00, 0.01, 0.05)

        # 0 users
        uptimeLine = 'top - 11:00:26 up 9 min,  0 users,  load average: 0.01, 0.05, 0.05'
        self.checkParseUptime(uptimeLine, '11:00:26', 9, 0, 0.01, 0.05, 0.05)


    def checkParseUptime(self, uptimeLine, timeOfDay, uptimeMinutes, numUsers, load1Min, load5Min, load15Min):
        """
        Parse uptime from the provided uptimeLine, and verify that the it parses
        the expected values that were provided.
        """
        entry = TopEntry()
        entry.parseUptime(uptimeLine)

        self.assertEqual(timeOfDay, entry.header[TopEntry.TIME_OF_DAY])
        self.assertEqual(uptimeMinutes, entry.header[TopEntry.UPTIME_MINUTES])
        self.assertEqual(numUsers, entry.header[TopEntry.NUM_USERS])
        self.assertEqual(load1Min, entry.header[TopEntry.LOAD_1_MINUTE])
        self.assertEqual(load5Min, entry.header[TopEntry.LOAD_5_MINUTES])
        self.assertEqual(load15Min, entry.header[TopEntry.LOAD_15_MINUTES])





if __name__ == '__main__':
    logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel)

    unittest.main()
