# -*- encoding: utf-8 -*-

from __future__ import absolute_import

from . import base
from .. import tasks


class EmailBackend(base.BaseEmailBackend):
    """
    Asynchronous email back-end that uses celery task for sending emails.
    """
    def send_messages(self, emails):
        return tasks.send_messages.delay(emails) if len(emails) else 0
