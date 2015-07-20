import datetime
import logging
import sys
import unittest

sys.path.append('../')

from top_parser import TopParser
from top_entry import TopEntry

logger = logging.getLogger(__name__)

class TopParserTestCase(unittest.TestCase):
    """ Tests for TopParser. """

    def testTopParser(self):
        """ Test the parse method """
        self.checkTopParser('data/topOneEntryWithDate.log', 1, datetime.date(datetime.date.today().year, 7, 20).toordinal())
        self.checkTopParser('data/topOneEntryNoDate.log', 1, self.getOrdinalDateFromUptimeDays(28))
        self.checkTopParser('data/top_30sec_20iter.log', 20, self.getOrdinalDateFromUptimeDays(27))

    def getOrdinalDateFromUptimeDays(self, uptimeDays):
        topEntry = TopEntry()
        return topEntry.getDateFromUptimeMinutes(uptimeDays * 24 * 60)

    def checkTopParser(self, testFile, numEntries, ordinalDate):
        """
        Validate the results of a TopParser invocation.
        :testFile - The name of the file to parse
        :numEntries - The expected number of parsed entries
        :ordinalDate - The ordinal date of the first entry, or None if there is no date.
        """
        topParser = TopParser(testFile)
        topParser.parse()
        self.assertEqual(numEntries, len(topParser.entries))

        logger.debug("Parsed entry: {0}".format(topParser.entries[0]))

        topEntry = topParser.entries[0]
        self.assertEqual(ordinalDate, topEntry.header[TopEntry.DATE])


if __name__ == '__main__':
    logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel)

    unittest.main()
