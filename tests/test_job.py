import logging
import sys
import unittest

sys.path.append('../')

from job import Job

class JobTestCase(unittest.TestCase):
    """ Tests for Job. """

    def testParse(self):
        """ Test the parse method """
        line = ' 1453 dpinkney  20   0 1983544 409608  44200 S  12.5  2.5 480:36.59 cinnamon'
        self.checkParse(line, '1453', 'dpinkney', '20', 0, 1983544, 409608, 44200, 'S', 12.5, 2.5,
                        '480:36.59', 'cinnamon')

        line = '  662 root      20   0  273524  86820  17340 S   6.2  0.5 338:15.30 Xorg'
        self.checkParse(line, '662', 'root', '20', 0, 273524, 86820, 17340, 'S', 6.2, 0.5, '338:15.30', 'Xorg')

        line = '    5 root       0 -20       0      0      0 S   0.0  0.0   0:00.00 kworker/0:0H'
        self.checkParse(line, '5', 'root', '0', -20, 0, 0, 0, 'S', 0.0, 0.0, '0:00.00', 'kworker/0:0H')

        line = '   10 root      rt   0       0      0      0 S   0.0  0.0   0:07.45 watchdog/0'
        self.checkParse(line, '10', 'root', 'rt', 0, 0, 0, 0, 'S', 0.0, 0.0, '0:07.45', 'watchdog/0')

        line = '  315 root      20   0  305080 123176 122940 S   0.0  0.8   5:58.17 systemd-journal'
        self.checkParse(line, '315', 'root', '20', 0, 305080, 123176, 122940, 'S', 0.0, 0.8, '5:58.17', 'systemd-journal')

        line = '  341 root     -51   0       0      0      0 S   0.0  0.0   0:00.00 irq/79-mei_me'
        self.checkParse(line, '341', 'root', '-51', 0, 0, 0, 0, 'S', 0.0, 0.0, '0:00.00', 'irq/79-mei_me')

        line = '  341 root     -51   0       0      0      0 S   0.0  0.0   1234:56 irq/79-mei_me'
        self.checkParse(line, '341', 'root', '-51', 0, 0, 0, 0, 'S', 0.0, 0.0, '1234:56', 'irq/79-mei_me')

        line = '23198 dpinkney  20   0  123656   2828   2360 R   6.2  0.0   0:00.01 top'
        self.checkParse(line, '23198', 'dpinkney', '20', 0, 123656, 2828, 2360, 'R', 6.2, 0.0, '0:00.01', 'top')
        line = '32469 dpinkney  20   0 3920412 2.403g  72804 S   6.2 15.4   2709:11 firefox'
        self.checkParse(line, '32469', 'dpinkney', '20', 0, 3920412, (2.403 * 1024 * 1024), 72804, 'S', 6.2, 15.4, '2709:11', 'firefox')

        line = '32469 dpinkney  20   0 3920412 1.234m  72804 S   6.2 15.4   2709:11 firefox'
        self.checkParse(line, '32469', 'dpinkney', '20', 0, 3920412, (1.234 * 1024), 72804, 'S', 6.2, 15.4, '2709:11', 'firefox')

    def checkParse(self, line, pid, user, priority, nice, virtual, resident, shared, status,
                   cpu, mem, cpuTime, command):
        job = Job()
        job.parse(line)

        self.assertEqual(pid, job.info[Job.JOB_PID])
        self.assertEqual(user, job.info[Job.JOB_USER])
        self.assertEqual(priority, job.info[Job.JOB_PR])
        self.assertEqual(nice, job.info[Job.JOB_NI])
        self.assertEqual(int(virtual), job.info[Job.JOB_VIRT])
        self.assertEqual(int(resident), job.info[Job.JOB_RES])
        self.assertEqual(int(shared), job.info[Job.JOB_SHR])
        self.assertEqual(status, job.info[Job.JOB_STATUS])
        self.assertEqual(cpu, job.info[Job.JOB_CPU])
        self.assertEqual(mem, job.info[Job.JOB_MEM])
        self.assertEqual(cpuTime, job.info[Job.JOB_TIME])
        self.assertEqual(command, job.info[Job.JOB_COMMAND])


if __name__ == '__main__':
    logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel)

    unittest.main()
