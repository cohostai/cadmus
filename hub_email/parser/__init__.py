#!/usr/bin/env python
# encoding: utf-8

import logging

from .utils import detect_ota
from .utils import OTA

from .airbnb import AIRBNB_EMAIL_PARSER
from .booking import BOOKING_EMAIL_PARSER
from .vrbo import VRBO_EMAIL_PARSER
from .exceptions import NotFoundOTASupportError
from .exceptions import DontParseEmailOTAError


logger = logging.getLogger(__name__)

MAP_PARSER = {
    OTA.AIRBNB_COM: AIRBNB_EMAIL_PARSER,
    OTA.BOOKING_COM: BOOKING_EMAIL_PARSER,
    OTA.VRBO_COM: VRBO_EMAIL_PARSER,
}


class EmailParser(object):

    @staticmethod
    def parse(sendgrid_data):
        ota = detect_ota(sendgrid_data)
        if not ota:
            raise NotFoundOTASupportError("Not found OTA for email")

        data = MAP_PARSER[ota].parse(sendgrid_data)
        if not data:
            raise DontParseEmailOTAError("Not parse email from ota: %s" % ota)

        data['email_id'] = sendgrid_data['email_id']
        return data


email_parser = EmailParser()
