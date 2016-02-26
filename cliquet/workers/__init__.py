class WorkersBase(object):
    """Background workers abstraction used by event listeners.
    """
    def apply_async(self, name, func, args=None, callback=None):
        """Run the specified `func` in background with the specified `args`
        and calls `callback` with the result.

        :param str name: an arbitrary identifier
        :param func func: a function to run in background
        :param tuple args: a list of parameters to provide to `func`
        :param func callback: the function to be called when task is done.
        """
        raise NotImplementedError()


def heartbeat(backend):
    """No-op heartbeat check for workers.
    XXX: find out a way to provide heartbeat feature.
    """
    return lambda r: True
