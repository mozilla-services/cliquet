from pyramid.threadlocal import get_current_registry


class ListenerBase(object):
    def _done(self, name, res_id, success, result):
        pass

    def _async_run(self, event):
        workers = get_current_registry().workers
        workers.apply_async('event', self._run, (event,), self._done)

    def _run(self, event):
        raise NotImplementedError()

    def __call__(self, event, async=True):
        """
        :param event: Incoming event
        :param async: Run asynchronously, default: True
        """
        if async:
            return self._async_run(event)
        else:
            # not used yet
            return self._run(event)     # pragma: no cover
