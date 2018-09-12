#!/usr/bin/env python
# encoding: utf-8
"""
messages

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from ..base import CascadingEmailParser
from ..base import HtmlEmailParserBase
from ..processor import PostProcessor
from ..utils import OTA
from ..utils import get_type_message
from ..utils import validate_required_parser


class MessageTemplate1(HtmlEmailParserBase):

    def __init__(self):
        HtmlEmailParserBase.__init__(
            self,
            required={
                'message': "//p[contains(@class, 'message-card message-card-gray')][normalize-space()]|"
                           "//p[contains(@class, 'message-card message-card-gray')]/img/@src",
                'from': "//a[contains(@href, '/users/show')]/p[contains(@class, 'heavy')]/text()",
                'thread_href': "//a[contains(@class,'btn-primary')]/@href",
                'listing_url': "//a[contains(@href, '/rooms/')]/@href",
            },
            optional={
                'checkin_str': "//table[@class='row'][2]//tr/th[contains(@class,'first')]/p[2]",
                'checkout_str': "//table[@class='row'][2]//tr/th[contains(@class,'last')]/p[2]",
                'user_id': "//a[contains(@href, 'users/show/')]/@href",
                'profile_url': "//a[contains(@href, 'users/show/')]/img/@src",
            },
            newline_fields=['message', ]
        )


class MessageEmailParser(CascadingEmailParser):

    required_fields = [
        'message', 'from', 'listing_id', 'message_thread_id',
    ]

    def __init__(self):
        CascadingEmailParser.__init__(self, [
            MessageTemplate1(),
        ])

    def parse(self, sendgrid_data):
        parsed_data = CascadingEmailParser.parse(self, sendgrid_data)
        if not parsed_data:
            return None

        PostProcessor.extract_thread_id_from_url(parsed_data)
        PostProcessor.extract_checkin_checkout_dates(parsed_data)
        PostProcessor.extract_reply_to_email(sendgrid_data, parsed_data)
        PostProcessor.extract_in_reply_to(sendgrid_data, parsed_data)
        PostProcessor.extract_references(sendgrid_data, parsed_data)
        PostProcessor.extract_listing_url(parsed_data)
        PostProcessor.extract_listing_id(parsed_data)
        PostProcessor.attach_team_info(parsed_data)
        PostProcessor.extract_profile_url(parsed_data)
        PostProcessor.extract_guest_first_name(sendgrid_data, parsed_data)
        PostProcessor.attach_host_first_name(parsed_data)
        PostProcessor.add_from_type_to_message(parsed_data)
        PostProcessor.extract_user_id(parsed_data)

        email_type = get_type_message(sendgrid_data['subject'])
        PostProcessor.attach_meta_email(parsed_data, OTA.AIRBNB_COM, email_type)

        if validate_required_parser(parsed_data, self.required_fields):
                return parsed_data
