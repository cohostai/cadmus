#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from ..base import CascadingEmailParser
from .cancellation import CancellationReservationEmailParser
from .change_reservation import ChangeReservationEmailParser
from .messages import MessageEmailParser
from .request_reservation import RequestReservationEmailParser
from .reservations import HostReservationParser


AIRBNB_EMAIL_PARSER = CascadingEmailParser([
    HostReservationParser(),
    MessageEmailParser(),
    CancellationReservationEmailParser(),
    ChangeReservationEmailParser(),
    RequestReservationEmailParser(),
])
