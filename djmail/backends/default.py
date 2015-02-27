# -*- encoding: utf-8 -*-

from __future__ import absolute_import

from . import base
from .. import core


class EmailBackend(base.BaseEmailBackend):
    """
    Default email back-end that sends e-mails synchronously.
    """
    def send_messages(self, emails):
        return core._send_messages(emails) if len(emails) else 0
