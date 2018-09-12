#!/usr/bin/env python
# encoding: utf-8
"""
request_reservation

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from ..base import CascadingEmailParser
from ..base import HtmlEmailParserBase
from ..processor import PostProcessor
from ..utils import OTA
from ..utils import EmailType
from ..utils import validate_required_parser


class RequestReservationTemplate1(HtmlEmailParserBase):
    def __init__(self):
        HtmlEmailParserBase.__init__(
            self,
            required={
                'from': "//a[contains(@href, 'abnb.me')]/p[contains(@class, 'heavy')]/text()",
                'reservation_href': "//a[contains(@class,'btn-primary')]/@href",
                'listing_picture_url': "//a[contains(@href, '/rooms/show')]/img/@src",
                'checkin_str': "//tr/th[contains(@class, 'small-5 large-5 columns first')]/p[2]",
                'checkout_str': "//tr/th[contains(@class, 'small-5 large-5 columns last')]/p[2]",
            },
            optional={
                'profile_url': "//img[@class='profile-img']/@src",
                'message': "//p[contains(@class, 'message-card message-card-gray')]",
            })


class RequestReservationEmailParser(CascadingEmailParser):

    required_fields = [
        'message', 'from', 'listing_id', 'reservation_code',
        'checkin', 'checkout'
    ]

    def __init__(self):
        CascadingEmailParser.__init__(self, [
            RequestReservationTemplate1(),
        ])

    def parse(self, sendgrid_data):
        parsed_data = CascadingEmailParser.parse(self, sendgrid_data)
        if not parsed_data:
            return None

        PostProcessor.extract_reservation_code_from_href(sendgrid_data, parsed_data)
        PostProcessor.extract_listing_id(parsed_data)
        PostProcessor.extract_checkin_checkout_dates(parsed_data)
        PostProcessor.extract_message_request_reservation(parsed_data)
        PostProcessor.populate_listing_id(parsed_data)
        PostProcessor.attach_meta_email(parsed_data, OTA.AIRBNB_COM, EmailType.REQUEST_RESERVATION)

        if validate_required_parser(parsed_data, self.required_fields):
            return parsed_data
