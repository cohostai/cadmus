#!/usr/bin/env python
# encoding: utf-8
"""
message

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from ..base import HtmlEmailParserBase
from ..processor import PostProcessor
from ..utils import OTA
from ..utils import EmailType
from ..utils import validate_required_parser


class MessageParser(HtmlEmailParserBase):
    required_fields = [
        'message', 'from', 'reservation_code', 'property',
        'checkin', 'checkout', 'reply_to'
    ]

    def __init__(self):
        HtmlEmailParserBase.__init__(self, required={
            'message': "//td[@bgcolor='#EDEDED']",
            'from': "//p[contains(text(), 'Guest name:')]/span",
            'checkin_str': "//p[contains(text(), 'Check-in:')]/span",
            'checkout_str': "//p[contains(text(), 'Check-out:')]/span",
            'reservation_code': "//p[contains(text(), 'Booking number:')]/span",
            'property': "//p[contains(text(), 'Property name:')]/span",
        }, optional={
        }, newline_fields=['message', ])

    def parse(self, sendgrid_data):
        parsed_data = HtmlEmailParserBase.parse(self, sendgrid_data)

        if not parsed_data:
            return None

        PostProcessor.extract_checkin_checkout_dates(parsed_data)
        PostProcessor.extract_reply_to_bk_email(sendgrid_data, parsed_data)
        PostProcessor.attach_meta_email(parsed_data, OTA.BOOKING_COM, EmailType.NORMAL_MESSAGE)

        if validate_required_parser(parsed_data, self.required_fields):
            return parsed_data
