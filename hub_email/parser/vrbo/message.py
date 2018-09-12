#!/usr/bin/env python
# encoding: utf-8
"""
message

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
        HtmlEmailParserBase.__init__(self, required={
            'listing_url': "//td[contains(text(), 'Property')]/../td[2]/div/span",
            'reservation_info': "//td[contains(text(), 'Dates')]/../td[2]/div/span/strong",
            'guest_name': "//td[contains(text(), 'Traveler name')]/../td/div",
            'message': "//p/strong[contains(text(), 'Message from')]/../following-sibling::p",
            'message_thread_url': "//a[contains(@href, '/rm/message')]/@href",
        }, optional={

        }, newline_fields=['message', ])


class MessageTemplate2(HtmlEmailParserBase):
    def __init__(self):
        HtmlEmailParserBase.__init__(self, required={
            'listing_url': "//td[contains(text(), 'Property')]/../td[2]/div/span",
            'reservation_info': "//td[contains(text(), 'Dates')]/../td[2]/div/span/strong",
            'guest_name': "//td[contains(text(), 'Traveler name')]/../td/div",
            'message': "//p[@class='content-spacer']",
            'message_thread_url': "//a[contains(@href, '/rm/message')]/@href",
        }, optional={

        }, newline_fields=['message', ])


class MessageTemplate3(HtmlEmailParserBase):
    def __init__(self):
        HtmlEmailParserBase.__init__(self, required={
            'listing_url': "//td[contains(text(), 'Property')]/../td[2]/div/span",
            'reservation_code': "//td[contains(text(), 'Reservation ID')]/../td[2]/div",
            'reservation_info': "//td[contains(text(), 'Dates')]/../td[2]/div/span/strong",
            'guest_name': "//td[contains(text(), 'Traveler name')]/../td/div",
            'message': "//td[@class='panel-bce']/table[@class='row'][2]//tr/td[@class='wrapper last']/table[@class='twelve columns']//tr/td[1]",
            'message_thread_url': "//a[contains(@href, '/rm/message')]/@href",
        }, optional={

        }, newline_fields=['message', ])


class MessageEmailParser(CascadingEmailParser):

    required_fields = ['checkin', 'checkout', 'listing_id', 'guest_name',
                       'guest_first_name', 'message', 'reply_to',
                       'message_thread_id', 'from']

    def __init__(self):
        CascadingEmailParser.__init__(self, [
            MessageTemplate1(),
            MessageTemplate2(),
            MessageTemplate3()
        ])

    def parse(self, sendgrid_data):
        parsed_data = CascadingEmailParser.parse(self, sendgrid_data)
        if parsed_data:
            PostProcessor.extract_listing_id(parsed_data)
            PostProcessor.extract_checkin_str_checkout_str(sendgrid_data, parsed_data)
            PostProcessor.extract_checkin_checkout_dates(parsed_data)
            PostProcessor.extract_reply_to_email(sendgrid_data, parsed_data)
            PostProcessor.extract_vrbo_message_thread_id(parsed_data)
            PostProcessor.extract_guest_first_name(sendgrid_data, parsed_data)
            PostProcessor.extract_from_user(sendgrid_data, parsed_data)
            PostProcessor.attach_team_info(parsed_data)
            PostProcessor.add_from_type_to_message(parsed_data)

            email_type = get_type_message(sendgrid_data['subject'])
            PostProcessor.attach_meta_email(parsed_data, OTA.VRBO_COM, email_type)

            if validate_required_parser(parsed_data, self.required_fields):
                return parsed_data

        return None
