#!/usr/bin/env python
# encoding: utf-8
"""
cancellation

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


class CancellationReservationTemplate1(HtmlEmailParserBase):
    def __init__(self):
        HtmlEmailParserBase.__init__(
            self,
            required={
                'reservation_info': "//table[@class='container']//table[@class='row']//tr/"
                                    "th[@class='small-12 large-12 columns first valign-mid']/p[@class='body-text light'][1]",
                'reservation_href': "//table[@class='container']//tr/td/div[6]/table[@class='row'][3]//tr/th/a/@href",
                'listing_href': "//table[@class='container']//tr/td/div[9]/table[@class='row']//tr/th/a/@href"
            },
            optional={
                'guest_name': "//table[@class='container']//table[@class='row']//a/p[@class='body-text heavy']"
            })


class CancellationReservationTemplate2(HtmlEmailParserBase):
    def __init__(self):
        HtmlEmailParserBase.__init__(
            self,
            required={
                'host_name': "//td[@class='container']/div[@class='content']/div[contains(@class,'section')]/p[1]|"
                             "//table[@class='container']//tr/td/div[2]/table[@class='row']//tr/th/p[1]",
                'content_cancel': "//td[@class='container']/div[@class='content']/div[contains(@class,'section')]/p[2]|"
                                  "//table[@class='container']//tr/td/div[3]/table[@class='row']//tr/th/p"
            }, optional={})


class CancellationReservationEmailParser(CascadingEmailParser):

    required_fields = ['reservation_code']

    def __init__(self):
        CascadingEmailParser.__init__(self, [
            CancellationReservationTemplate1(),
            CancellationReservationTemplate2()
        ])

    def parse(self, sendgrid_data):
        parsed_data = CascadingEmailParser.parse(self, sendgrid_data)

        if parsed_data:
            PostProcessor.extract_checkin_str_checkout_str(sendgrid_data, parsed_data)
            PostProcessor.extract_checkin_checkout_dates(parsed_data)
            PostProcessor.extract_reservation_code_from_href(sendgrid_data, parsed_data)
            PostProcessor.extract_listing_id_cancel(parsed_data)
            PostProcessor.attach_meta_email(parsed_data, OTA.AIRBNB_COM, EmailType.CANCELLATION_RESERVATION)

            if validate_required_parser(parsed_data, self.required_fields):
                return parsed_data

        return None
