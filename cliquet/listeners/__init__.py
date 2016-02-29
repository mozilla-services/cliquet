import copy


class ListenerBase(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, event):
        """
        :param event: Incoming event
        """
        raise NotImplementedError()

    def done(self, name, res_id, success, result):
        from cliquet import logger
        logger.info("Async listener done.",
                    name=name,
                    result_id=res_id,
                    success=success,
                    result=result)


def async_listener(workers, listener, callback, event):
    """
    Execute the specified `listener` on the background workers.
    """
    # With asynchronous listeners, the `event` is serialized (pickled).
    # Since :class:`pyramid.utils.Request` is not pickable, we set it
    # to None.
    event = copy.copy(event)
    event.request = None
    workers.apply_async('event', listener, (event,), callback)
