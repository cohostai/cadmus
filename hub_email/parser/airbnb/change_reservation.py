#!/usr/bin/env python
# encoding: utf-8
"""
change_reservation

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from ..base import HtmlEmailParserBase
from ..processor import PostProcessor
from ..utils import OTA
from ..utils import EmailType
from ..utils import validate_required_parser


class ChangeReservationEmailParser(HtmlEmailParserBase):

    required_fields = [
        'guest_name', 'reservation_code', 'original_checkin',
        'original_checkout', 'requested_checkin', 'requested_checkout'
    ]

    def __init__(self):
        HtmlEmailParserBase.__init__(
            self,
            required={
                "guest_name": "//a/p[contains(@class, 'heavy')]",
                "reservation_href": "//a[contains(@href, '/reservation/itinerary')]/@href",
                "property": "//a/p[contains(@class, 'light')][2]",
                "original_dates": "//tr[@class='change-diff-card-text']/td[contains(@class, 'change-diff-card-original')]",
                "requested_dates": "//tr[@class='change-diff-card-text']/td[contains(@class, 'change-diff-card-requested')]"
            },
            optional={}
        )

    def parse(self, sendgrid_data):
        parsed_data = HtmlEmailParserBase.parse(self, sendgrid_data)
        if not parsed_data:
            return None

        PostProcessor.extract_reservation_code_from_href(sendgrid_data, parsed_data)

        # TODO handle extract request change dates
        PostProcessor.extract_original_dates(parsed_data)
        PostProcessor.extract_requested_dates(parsed_data)
        PostProcessor.attach_meta_email(parsed_data, OTA.AIRBNB_COM, EmailType.REQUEST_CHANGE_RESERVATION)

        if validate_required_parser(parsed_data, self.required_fields):
            return parsed_data
