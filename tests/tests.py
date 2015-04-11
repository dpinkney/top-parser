import logging
import sys
import unittest

sys.path.append('../')

from test_top_entry import TopEntryTestCase
from test_job import JobTestCase

if __name__ == '__main__':
    logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel)

    unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TopEntryTestCase),
                        unittest.TestLoader().loadTestsFromTestCase(JobTestCase)
                        ])
    unittest.main()
    
