#!/usr/bin/env python
# encoding: utf-8
"""
utils

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from chocon.utils.regex import extract_from_regex


class AirbnbUserType(object):
    COHOST = 'cohost'
    HOST = 'host'
    GUEST = 'guest'
    BOT = 'bot'


def get_primary_host_for_listing(listing_id):
    pass
    # info = get_listing_info(listing_id)
    # if info:
    #     return get_json_path(info, 'primary_host')


def get_picture_url_id(picture_url):
    picture_id = extract_from_regex(
        picture_url,
        r".*pictures/(.*)\..*",
        1
    )
    return str(picture_id) if picture_id else None
