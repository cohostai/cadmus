#!/usr/bin/env python
# encoding: utf-8
"""
post_processor

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import re
import urllib
import urlparse
from email.parser import HeaderParser

import requests

from .airbnb.constants import SUBJECT_EMAILS_INSTANT_BOOK
from .airbnb.utils import AirbnbUserType
from .airbnb.utils import get_primary_host_for_listing
from .utils import date as date_utils
from .utils.email import get_guest_first_name
from .utils.email import get_in_reply_to
from .utils.email import get_references
from .utils.email import get_reply_to_address
from .utils.email import parse_checkin_checkout
from .utils.regex import extract_from_regex

logger = logging.getLogger(__name__)


class PostProcessor(object):

    @classmethod
    def attach_meta_email(cls, parsed_data, source, email_type):
        parsed_data['source'] = source
        parsed_data['email_type'] = email_type

    @classmethod
    def extract_thread_id_from_url(cls, parsed_data):
        if not parsed_data['thread_href']:
            return

        parsed_data["message_thread_id"] = extract_from_regex(
            parsed_data['thread_href'],
            r"https://.*/z/q/(\d+)\?", 1)

    @classmethod
    def extract_checkin_checkout_dates(cls, parsed_data):
        if parsed_data.get('checkin_str'):
            checkin = date_utils.versatile_date_parse(
                parsed_data['checkin_str'])
            if checkin:
                parsed_data['checkin'] = checkin.date().isoformat()
        if parsed_data.get('checkout_str'):
            checkout = date_utils.versatile_date_parse(
                parsed_data['checkout_str'])
            if checkout:
                parsed_data['checkout'] = checkout.date().isoformat()

    @classmethod
    def extract_listing_url(cls, parsed_data):
        if not parsed_data.get('listing_url'):
            return
        parsed_data['listing_url'] = urllib.unquote(parsed_data['listing_url'])

        parsed = urlparse.urlparse(parsed_data['listing_url'])
        params = urlparse.parse_qs(parsed.query)
        if params.get('$original_url'):
            parsed_data['listing_url'] = ''.join(params.get('$original_url'))

    @classmethod
    def extract_reservation_code(cls, parsed_data):
        if not parsed_data['reservation_code']:
            return
        parsed_data['reservation_code'] = extract_from_regex(
            parsed_data['reservation_code'],
            r'\b([A-Z]|[0-9]){1,}\b', 0)

    @classmethod
    def extract_listing_id(cls, parsed_data):
        if not parsed_data.get('listing_url'):
            return

        patterns = [
            r"(?<=rooms\/)(\d+).*",
            r"(?<=rooms\/show\/)(\d+).*",
            r".*rooms\/show.*id=(\d+).*",
            r"(?<=vrbo.com\/)(\d+).*",
            r"^#(\d+)$",
        ]

        for pattern in patterns:
            listing_id = extract_from_regex(parsed_data['listing_url'], pattern, 1)
            if listing_id:
                parsed_data['listing_id'] = listing_id
                break

    @classmethod
    def extract_host_name(cls, parsed_data):
        if not parsed_data.get('host_name'):
            return
        host_name = extract_from_regex(
            parsed_data['host_name'],
            r"(.+)is your host", 1)

        parsed_data['host_name'] = host_name or parsed_data['host_name']

    @classmethod
    def attach_host_first_name(cls, parsed_data):
        if parsed_data.get('host_first_name'):
            return
        if not parsed_data.get('listing_id'):
            return
        listing_id = parsed_data['listing_id']
        primary_host = get_primary_host_for_listing(listing_id)
        if primary_host:
            parsed_data['host_first_name'] = primary_host['first_name']

    @classmethod
    def extract_reply_to_email(cls, sendgrid_data, parsed_data):
        reply_to = get_reply_to_address(sendgrid_data['headers'])
        if reply_to:
            parsed_data['reply_to'] = reply_to

    @classmethod
    def extract_guest_first_name(cls, sendgrid_data, parsed_data):
        guest_first_name = get_guest_first_name(sendgrid_data['headers'])
        if guest_first_name:
            parsed_data['guest_first_name'] = guest_first_name

    @classmethod
    def extract_in_reply_to(cls, sendgrid_data, parsed_data):
        in_reply_to = get_in_reply_to(sendgrid_data['headers'])
        if in_reply_to:
            parsed_data['in_reply_to'] = in_reply_to

    @classmethod
    def extract_references(cls, sendgrid_data, parsed_data):
        references = get_references(sendgrid_data['headers'])
        if references:
            parsed_data['references'] = references

    @classmethod
    def attach_team_info(cls, parsed_data):
        # TODO: populate team info
        pass

        # try:
        #     utils.attach_team_info(parsed_data)
        # except Exception as e:
        #     logging.warn('Failed to attach team info: %s', e)

    @classmethod
    def extract_profile_url(cls, parsed_data):
        if not parsed_data.get('profile_url'):
            return
        profile_url = parsed_data['profile_url']
        parsed_data['profile_url'] = profile_url.rsplit('?')[0]

    @classmethod
    def extract_checkin_str_checkout_str(cls, sendgrid_data, parsed_data):
        if parsed_data.get('reservation_info'):
            checkin_str, checkout_str = parse_checkin_checkout(
                parsed_data['reservation_info'])

            if checkin_str:
                parsed_data['checkin_str'] = checkin_str

            if checkout_str:
                parsed_data['checkout_str'] = checkout_str

            del parsed_data['reservation_info']
        else:
            cls.extract_checkin_cancel_email(sendgrid_data, parsed_data)

    @classmethod
    def extract_checkin_cancel_email(cls, sendgrid_data, parsed_data):
        regex = r"Reservation \w+ on (.+?) Canceled"
        checkin_str = extract_from_regex(sendgrid_data['subject'], regex, 1)
        if checkin_str:
            parsed_data['checkin_str'] = checkin_str
        elif 'content_cancel' in parsed_data:
            regex = r".*(\d{4}-\d{1,2}-\d{1,2}).*"
            checkin_str = extract_from_regex(
                parsed_data['content_cancel'],
                regex,
                1
            )

            if checkin_str:
                parsed_data['checkin_str'] = checkin_str

    @classmethod
    def extract_short_link(cls, short_link):
        if not short_link:
            return None
        patt = re.compile(".*abnb\.me.*")
        match = patt.match(short_link)
        if not match:
            return short_link
        res = requests.get(short_link, allow_redirects=False)
        link = extract_from_regex(
            res.text,
            r".*validate\(\"(http.*)\"\).*",
            1
        )
        return link or short_link

    @classmethod
    def extract_reservation_code_from_href(cls, sendgrid_data, parsed_data):
        expand_link = cls.extract_short_link(parsed_data.get('reservation_href'))

        patterns = [
            r".*/z/a/(\w+)\??.*",
            r"code=(\w+)&?",
        ]
        reservation_code = None
        for pattern in patterns:
            reservation_code = extract_from_regex(
                expand_link,
                pattern,
                1
            )
            if reservation_code:
                break

        if reservation_code:
            parsed_data['reservation_code'] = reservation_code
            del parsed_data['reservation_href']
        else:
            # Parse from subject of email
            reservation_code = extract_from_regex(
                sendgrid_data['subject'],
                r"Reservation ([\w]+) on",
                1
            )
            if reservation_code:
                parsed_data['reservation_code'] = reservation_code
            elif 'content_cancel' in parsed_data:
                reservation_code = extract_from_regex(
                    parsed_data['content_cancel'],
                    r".*\((.+)\).*",
                    1
                )
                if reservation_code:
                    parsed_data['reservation_code'] = reservation_code

                del parsed_data['content_cancel']

    @classmethod
    def extract_listing_id_cancel(cls, parsed_data):
        if not parsed_data.get('listing_href'):
            return

        listing_id = extract_from_regex(
            parsed_data['listing_href'],
            r"manage-listing/(\d+)/calendar",
            1
        )
        if listing_id:
            parsed_data['listing_id'] = listing_id

        del parsed_data['listing_href']

    @classmethod
    def add_from_type_to_message(cls, parsed_data):
        if parsed_data.get('from') == parsed_data.get('guest_first_name'):
            from_type = AirbnbUserType.GUEST
        elif parsed_data.get('from') == parsed_data.get('host_first_name'):
            from_type = AirbnbUserType.HOST
        else:
            from_type = AirbnbUserType.COHOST

        parsed_data['from_type'] = from_type

    @classmethod
    def extract_listing_id_from_manage_url(cls, parsed_data):
        if parsed_data.get('manage_listing_url'):
            patterns = [
                r"https://.*airbnb.*/manage-listing/(\d+)\?",
                r"https://.*airbnb.*/rooms/show.*id=(\d+).*"
            ]
            for pattern in patterns:
                listing_id = extract_from_regex(
                    parsed_data['manage_listing_url'],
                    pattern,
                    1
                )
                if listing_id:
                    parsed_data['listing_id'] = listing_id
                    break

    @classmethod
    def extract_reservation_type(cls, sendgrid_data, parsed_data):
        subject_email = sendgrid_data['subject']
        for subject in SUBJECT_EMAILS_INSTANT_BOOK:
            if subject_email.startswith(subject):
                parsed_data['reservation_type'] = 'instant_book'
                return
        parsed_data['reservation_type'] = 'normal_book'

    @classmethod
    def extract_original_dates(cls, parsed_data):
        if parsed_data.get('original_dates'):
            original_checkin_str, original_checkout_str = parse_checkin_checkout(parsed_data['original_dates'])
            if original_checkin_str and original_checkout_str:
                original_checkin = date_utils.versatile_date_parse(
                    original_checkin_str.encode('ascii', 'ignore')
                )

                original_checkout = date_utils.versatile_date_parse(
                    original_checkout_str.encode('ascii', 'ignore')
                )

                if original_checkin and original_checkout:
                    parsed_data['original_checkin'] = original_checkin.date().isoformat()
                    parsed_data['original_checkout'] = original_checkout.date().isoformat()

            del parsed_data['original_dates']

    @classmethod
    def extract_requested_dates(cls, parsed_data):
        if parsed_data.get('requested_dates'):
            requested_checkin_str, requested_checkout_str = parse_checkin_checkout(
                parsed_data['requested_dates']
            )
            if requested_checkin_str and requested_checkout_str:
                requested_checkin = date_utils.versatile_date_parse(
                    requested_checkin_str.encode('ascii', 'ignore')
                )

                requested_checkout = date_utils.versatile_date_parse(
                    requested_checkout_str.encode('ascii', 'ignore')
                )

                if requested_checkin and requested_checkout:
                    parsed_data['requested_checkin'] = requested_checkin.date().isoformat()
                    parsed_data['requested_checkout'] = requested_checkout.date().isoformat()

            del parsed_data['requested_dates']

    @classmethod
    def extract_user_id(cls, parsed_data):
        if parsed_data.get('user_id'):
            patterns = [
                r".*show/(\d+).*",
                r".*users.*id=(\d+).*"
            ]

            for pattern in patterns:
                user_id = extract_from_regex(
                    parsed_data['user_id'],
                    pattern,
                    1
                )
                if user_id:
                    parsed_data['user_id'] = user_id

    @classmethod
    def extract_message_request_reservation(cls, parsed_data):
        message = "REMINDER REQUEST RESERVATION: \n"
        if parsed_data.get('message'):
            message = "%s \"%s\"" % (message, parsed_data['message'])
        message = "%s\n%s" % (
            message,
            "Please login on airbnb to accept this reservation. \nDO NOT REPLY THIS MESSAGE"
        )

        parsed_data['message'] = message

    @classmethod
    def extract_reply_to_bk_email(cls, sendgrid_data, parsed_data):
        headers = sendgrid_data['headers']
        headers = headers.encode('utf8')
        reply_to_1 = get_reply_to_address(headers)
        parsed_headers = HeaderParser().parsestr(headers)
        reply_to_2 = None
        if parsed_headers.get('Reply-To'):
            reply_to_2 = parsed_headers['Reply-To']
        reply_to = reply_to_1 or reply_to_2
        if reply_to:
            parsed_data['reply_to'] = reply_to

    @classmethod
    def populate_listing_id(cls, parsed_data):
        pass
        # if not parsed_data.get('listing_picture_url'):
        #     return
        #
        # picture_id = get_picture_url_id(parsed_data['listing_picture_url'])
        # if not picture_id:
        #     logger.error("Not extract picture id ")
        #     return
        #
        # # TODO: get listing info
        # listing = es_client.get_listing_from_picture_id(picture_id)
        # if not listing:
        #     logging.error("Not found listing with picture id: %s" % picture_id)
        #     return
        # parsed_data['listing_id'] = listing['id']
        # del parsed_data['listing_picture_url']

    @classmethod
    def extract_vrbo_message_thread_id(cls, parsed_data):
        if not parsed_data.get('message_thread_url'):
            return

        path = urlparse.urlparse(parsed_data['message_thread_url']).path
        pattern = r".*/(.*)$"
        message_thread_id = extract_from_regex(path, pattern, 1)
        if message_thread_id:
            parsed_data['message_thread_id'] = message_thread_id

        del parsed_data['message_thread_url']

    @classmethod
    def extract_from_user(cls, sendgrid_data, parsed_data):
        from_email = sendgrid_data.get('from') or ''
        sender_name = extract_from_regex(from_email, r"\"'(.*)' via .*", 1)
        if sender_name:
            parsed_data['from'] = sender_name
