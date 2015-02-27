# -*- encoding: utf-8 -*-

from __future__ import absolute_import

from . import base
from .. import core


class EmailBackend(base.BaseEmailBackend):
    """
    Default email back-end that sends e-mails synchronously.
    """
    def send_messages(self, email_messages):
        return core._send_messages(email_messages) if len(email_messages) else 0
