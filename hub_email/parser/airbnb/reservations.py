#!/usr/bin/env python
# encoding: utf-8
"""
reservations

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


class HostReservationConfirmedTemplate1(HtmlEmailParserBase):

    def __init__(self):
        HtmlEmailParserBase.__init__(
            self,
            required={
                'checkin_str': "//p[contains(text(), 'C‌h‌e‌c‌k‌-‌i‌n‌')]/preceding-sibling::p[1]/text()",
                'checkout_str': "//p[contains(text(), 'C‌h‌e‌c‌k‌o‌u‌t‌')]/preceding-sibling::p[1]/text()",
                'reservation_code': "//p[contains(text(), 'Confirmation code')]/following-sibling::p/text()",
                'manage_listing_url': "//p[@class='headline light']/../@href",
                'thread_href': "//a[contains(@class,'btn-primary')]/@href",
                'property': "//p[@class='headline light']/text()",
                'guest_name': "//a[contains(@href, '/users/show')]/p[contains(@class, 'heavy')]/text()",
                'earning': "//p[contains(text(), 'Total')]/../following-sibling::th/p/text()",
            },
            optional={
                'profile_url': "//img[@class='profile-img']/@src",
                'message': "//p[contains(@class, 'message-card message-card-gray')]",
                'user_id': "//img[@class='profile-img']/../@href",
            },
            newline_fields=['message', ]
        )


class HostReservationParser(CascadingEmailParser):

    required_fields = [
        'checkin', 'checkout', 'reservation_code',
        'listing_id', 'message_thread_id', 'property',
        'guest_name', 'earning', 'reservation_type'
    ]

    def __init__(self):
        CascadingEmailParser.__init__(self, [
            HostReservationConfirmedTemplate1(),
        ])

    def parse(self, sendgrid_data):
        parsed_data = CascadingEmailParser.parse(self, sendgrid_data)
        if not parsed_data:
            return None

        PostProcessor.extract_listing_id_from_manage_url(parsed_data)
        PostProcessor.extract_thread_id_from_url(parsed_data)
        PostProcessor.extract_checkin_checkout_dates(parsed_data)
        PostProcessor.extract_reply_to_email(sendgrid_data, parsed_data)
        PostProcessor.extract_reservation_type(sendgrid_data, parsed_data)
        PostProcessor.extract_user_id(parsed_data)
        PostProcessor.attach_team_info(parsed_data)
        PostProcessor.attach_meta_email(parsed_data, OTA.AIRBNB_COM, EmailType.BOOKING_CONFIRMATION)

        if validate_required_parser(parsed_data, self.required_fields):
            return parsed_data
