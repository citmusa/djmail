# -*- encoding: utf-8 -*-


class BaseEmailBackend(object):
    """
    Base class that implements a Django email back-end interface.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def open(self):
        pass

    def close(self):
        pass

    def send_messages(self, emails):
        raise NotImplementedError
