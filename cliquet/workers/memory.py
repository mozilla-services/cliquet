import os
import signal
import traceback
from uuid import uuid4
from multiprocessing import Pool
from functools import partial
from collections import defaultdict, OrderedDict

from . import WorkersBase

try:
    # until dill works with pypy, let's use plain Pickle.
    # https://github.com/uqfoundation/dill/issues/73

    # we have, however, to implememt the pickling on locks
    # because of the Redis listener.
    #
    # The code below was inspired from dill
    import __pypy__         # NOQA
    from pickle import loads, dumps, Pickler, UnpicklingError
    from thread import LockType

    def _create_lock(locked, *args):
        from threading import Lock
        lock = Lock()
        if locked:
            if not lock.acquire(False):
                raise UnpicklingError("Cannot acquire lock")
        return lock

    def _save_lock(pickler, obj):
        pickler.save_reduce(_create_lock, (obj.locked(),), obj=obj)

    Pickler.dispatch[LockType] = _save_lock
except ImportError:     # pragma: no cover
    from dill import loads, dumps


def _run(dumped):       # pragma: no cover
    func, args = loads(dumped)
    try:
        result = func(*args)
    except Exception:
        return False, traceback.format_exc()
    return True, result


class Workers(WorkersBase):
    def __init__(self, size=1, result_size_limit=100):
        self.closed = True
        self.initialize(size, result_size_limit)

    def initialize(self, size=1, result_size_limit=100):
        if not self.closed:
            self.close()
        self.result_size_limit = 100
        self.size = size
        self._results = OrderedDict()
        self._in_progress = defaultdict(list)
        handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            self._pool = Pool(self.size, initializer=self._init_proc,
                              initargs=(os.environ,))
        finally:
            signal.signal(signal.SIGINT, handler)
        self.closed = False

    def get_result(self, res_id):
        return self._results[res_id]

    def _store_result(self, name, res_id, res, callback=None):
        while len(self._results) >= self.result_size_limit:
            self._results.popitem()

        self._in_progress[name].remove(res_id)
        success, result = res
        self._results[res_id] = res
        if not success:
            from cliquet import logger
            logger.error(result)

        if callback is not None:        # pragma: no cover
            callback(name, res_id, success, result)

    def _init_proc(self, environ):      # pragma: no cover
        os.environ.update(environ)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def in_progress(self, name):
        return self._in_progress[name]

    def close(self):
        self._pool.close()
        self._pool.join()
        self.closed = True

    def apply_async(self, name, func, args=None, callback=None):
        if args is None:
            args = tuple()
        res_id = str(uuid4())
        self._in_progress[name].append(res_id)
        async_callback = partial(self._store_result, name, res_id,
                                 callback=callback)
        cmd = partial(_run, dumps((func, args)))
        try:
            self._pool.apply_async(cmd, callback=async_callback)
        except KeyboardInterrupt:
            self._pool.terminate()
            self._pool.join()
            self.closed = True

        return res_id


_WORKERS_PER_PROCESS = {}


def load_from_config(config):
    settings = config.get_settings()
    num_workers = int(settings.get('background.processes', 1))
    pid = os.getpid()
    if pid in _WORKERS_PER_PROCESS:
        workers = _WORKERS_PER_PROCESS[pid]
        if workers.closed:
            workers.initialize(num_workers)
    else:
        _WORKERS_PER_PROCESS[pid] = workers = Workers(num_workers)

    return workers
