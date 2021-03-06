# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import functools
from concurrent.futures import Future, ThreadPoolExecutor
from django.db import connection

from . import base
from .. import core

# TODO: parametrize this
executor = ThreadPoolExecutor(max_workers=1)


def _close_connection_on_finish(function):
    """
    Decorator for future task, that closes django database connection when it ends.
    """
    @functools.wraps(function)
    def _decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        finally:
            connection.close()

    return _decorator


class EmailBackend(base.BaseEmailBackend):
    """
    Asynchronous email back-end that uses a thread pool for sending emails.
    """
    def send_messages(self, emails):
        if len(emails) == 0:
            future = Future()
            future.set_result(0)
            return future

        @_close_connection_on_finish
        def _send(messages):
            return core._send_messages(emails)

        return executor.submit(_send, emails)
