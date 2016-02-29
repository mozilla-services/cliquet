from cliquet import logger


class ListenerBase(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, event):
        """
        :param event: Incoming event
        """
        raise NotImplementedError()

    def done(self, name, res_id, success, result):
        logger.info("Async listener done.",
                    name=name,
                    result_id=res_id,
                    success=success,
                    result=result)


def async_listener(workers, listener, callback, event):
    workers.apply_async('event', listener, (event,), callback)
