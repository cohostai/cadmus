#!/usr/bin/env python
# encoding: utf-8
"""
email

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import base64
import re
from email.parser import HeaderParser

from .regex import extract_from_regex


class OTA(object):
    AIRBNB_COM = 'airbnb.com'
    BOOKING_COM = 'booking.com'
    VRBO_COM = 'vrbo.com'


class EmailType(object):
    BOOKING_CONFIRMATION = 'booking_confirmation'
    INQUIRY_MESSAGE = 'inquiry_message'
    NORMAL_MESSAGE = 'normal_message'
    REQUEST_RESERVATION = 'request_reservation'
    CANCELLATION_RESERVATION = 'cancellation_reservation'
    REQUEST_CHANGE_RESERVATION = 'request_change_reservation'


def validate_required_parser(parsed_data, fields_required):
    if not fields_required:
        return True

    if not isinstance(parsed_data, dict):
        return False

    fields_missing = [
        field for field in fields_required
        if ((field not in parsed_data) or (not parsed_data.get(field)))
    ]

    if fields_missing:
        return False

    return True


def get_reply_to_address(email_headers):
    email_headers = email_headers.encode('utf8')
    parsed_headers = HeaderParser().parsestr(email_headers)
    if parsed_headers.get('Reply-To'):
        reply_to = extract_from_regex(parsed_headers['Reply-To'],
                                      r"(.+) <(.+)>", 2)
        if reply_to:
            return reply_to

    return None


def b64normalize(b64string):
    paddings = (4 - (len(b64string) % 4)) % 4
    if paddings:
        return b64string + '=' * paddings

    return b64string


def b64decode_email_header_value(header_value, encoding='utf-8',
                                 unicode_return=True):
    if not header_value:
        return None

    header_value = header_value.strip()
    if not isinstance(header_value, str):
        header_value = header_value.encode(encoding)

    if (header_value.startswith('=?UTF-8?B?')
        or header_value.startswith('=?utf-8?B?')):
        prefix = header_value[:10]
        b64string = header_value.replace(prefix, '').replace('?=', '')
        b64string = b64normalize(b64string)
        header_value = base64.b64decode(b64string)

    return header_value.decode('utf-8') if unicode_return else header_value


def get_guest_first_name(email_headers):
    """
    Get guest first name from Reply-to headers.
    Ex: "Do Viet (Airbnb)" <26d6okv5b4cvh5fbnulsf0mitvfk@reply.airbnb.com>
    """
    email_headers = email_headers.encode('utf8')
    parsed_headers = HeaderParser().parsestr(email_headers)
    if parsed_headers.get('Reply-To'):
        patterns = [
            r'"(.+) \(.+\)" <(.+)>',
            r'(.*) <(.+)>',
        ]
        guest_first_name = None
        for pattern in patterns:
            guest_first_name = extract_from_regex(
                parsed_headers['Reply-To'], pattern, 1)
            if guest_first_name:
                break

        return b64decode_email_header_value(guest_first_name)


def get_in_reply_to(email_headers):
    email_headers = email_headers.encode('utf8')
    parsed_headers = HeaderParser().parsestr(email_headers)
    return parsed_headers.get('In-Reply-To')


def get_references(email_headers):
    email_headers = email_headers.encode('utf8')
    parsed_headers = HeaderParser().parsestr(email_headers)
    return parsed_headers.get('References')


def parse_checkin_checkout(checkin_checkout_str):
    """
    Parse checkin checkout patterns:
        Aug 16 - 18, 2017 · 3 guests
        Aug 16 - Sep 18, 2017 · 3 guests
        Aug 16, 2016 - Sep 18, 2017 · 3 guests

    :param checkin_checkout_str:
    :return:
    """
    checkin_checkout_str = checkin_checkout_str.strip()
    if not checkin_checkout_str:
        return None, None

    patterns = [
        "([a-zA-Z]+) (\d{1,2}) ?- ?(\d{1,2}), (\d{4}).*",
        "([a-zA-Z]+) (\d{1,2}) ?- ?([a-zA-Z]+) (\d{1,2}), (\d{4}).*",
        "([a-zA-Z]+) (\d{1,2}), (\d{4}) ?- ?([a-zA-Z]+) (\d{1,2}), (\d{4}).*"
    ]

    checkin_str, checkout_str = None, None
    for pattern in patterns:
        match = re.match(pattern, checkin_checkout_str)
        if match:
            lenght_group = len(match.groups())
            if lenght_group == 4:
                month, d_in, d_out, year = match.groups()
                checkin_str = '%s %s, %s' % (month[:3], d_in, year)
                checkout_str = '%s %s, %s' % (month[:3], d_out, year)

            if lenght_group == 5:
                m_in, d_in, m_out, d_out, year = match.groups()
                checkin_str = '%s %s, %s' % (m_in[:3], d_in, year)
                checkout_str = '%s %s, %s' % (m_out[:3], d_out, year)

            if lenght_group == 6:
                m_in, d_in, year_in, m_out, d_out, year_out = match.groups()
                checkin_str = '%s %s, %s' % (m_in[:3], d_in, year_in)
                checkout_str = '%s %s, %s' % (m_out[:3], d_out, year_out)
            break

    return checkin_str, checkout_str


def detect_ota(sendgrid_data):
    email_headers = sendgrid_data.get('headers')
    if not email_headers:
        return None

    email_headers = email_headers.encode('utf8')
    parsed_headers = HeaderParser().parsestr(email_headers)
    x_original_sender = parsed_headers.get('X-Original-Sender')

    if not x_original_sender:
        return None

    if 'airbnb.com' in x_original_sender:
        return OTA.AIRBNB_COM

    if 'messages.homeaway.com' in x_original_sender:
        return OTA.VRBO_COM

    if 'booking.com' in x_original_sender:
        return OTA.BOOKING_COM

    return None


def is_inquiry_message(subject):
    list_prefix = ("Inquiry", )
    return subject.startswith(list_prefix)


def get_type_message(subject):
    if is_inquiry_message(subject):
        email_type = EmailType.INQUIRY_MESSAGE
    else:
        email_type = EmailType.NORMAL_MESSAGE
    return email_type
