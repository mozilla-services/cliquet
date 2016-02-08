import unittest
import time
from cliquet.workers import MemoryWorkers


def boom():
    raise Exception('ok')


class TestMemoryWorkers(unittest.TestCase):
    def setUp(self):
        self.workers = MemoryWorkers(size=1)

    def tearDown(self):
        self.workers.close()

    def test_async(self):
        workers = self.workers
        workers.apply_async('some-sleep', time.sleep, (.2,))
        pids = workers.in_progress('some-sleep')
        self.assertEqual(len(pids), 1)
        time.sleep(.3)
        self.assertEqual(workers.in_progress('some-sleep'), [])

    def test_async_fails(self):
        workers = self.workers
        res_id = workers.apply_async('exc', boom)
        time.sleep(.2)
        res = workers.get_result(res_id)
        self.assertFalse(res[0])
        self.assertTrue('Traceback' in res[1])

    def test_initialize(self):
        workers = self.workers
        workers.initialize(2)
        self.assertEqual(workers.size, 2)

    def test_keyboardinterrupt(self):
        def _break(*args, **kw):
            raise KeyboardInterrupt()

        self.workers._pool.apply_async = _break
        self.workers.apply_async('ok', object())
        self.assertTrue(self.workers.closed)

    def test_result_size(self):
        # make sure the results don't grow indefinitely
        def noop(num):
            return num

        res_ids = [self.workers.apply_async('noop', noop, (i,))
                   for i in range(101)]

        while self.workers.in_progress('noop'):
            time.sleep(.1)
        time.sleep(.1)

        # one should be gone
        counter = error = 0
        for res_id in res_ids:
            try:
                self.workers.get_result(res_id)
                counter += 1
            except KeyError:
                error += 1

        self.assertEqual(counter, 100)
        self.assertEqual(error, 1)
