#!/usr/bin/env python
# encoding: utf-8
"""
date

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from datetime import date
from datetime import datetime
from datetime import timedelta

import dateparser
import humanize
import pytz
from dateutil import parser
from dateutil import relativedelta
from pytz import timezone


def nomalize_date_str(date_str):
    special_characters = [u"\u200c", ]
    for character in special_characters:
        date_str = date_str.replace(character, u"")

    return date_str


def format_date_in_utc(dt):
    return iso_format_date(pytz.utc.localize(dt))


def iso_format_date(dt):
    return dt.strftime("%Y-%m-%d")


def days_since_1970(dtdate):
    return (dtdate - date(1970, 1, 1)).days


def parse_iso_date(date_value):
    """Parse datetime from iso date string
    Args:
        date_value (str|date|datetime): a string in iso format or
            a date/datetime object
    Returns:
         datetime: parsed from date_value
    """
    if isinstance(date_value, datetime):
        return date_value

    if isinstance(date_value, date):
        return datetime(date_value.year, date_value.month, date_value.day)

    if not isinstance(date_value, basestring):
        return None

    try:
        return parser.parse(date_value)  # or use iso8601 module
    except Exception as e:
        return None


ACCEPTED_FORMAT_FULL = ['%a, %B %d, %Y',
                        '%a, %b %d, %Y',
                        '%A, %B %d, %Y',
                        '%b %d, %Y',
                        '%B %d, %Y',
                        '%Y-%m-%d',
                        '%m-%d-%Y',
                        '%d-%m-%Y']
# https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
ACCEPTED_FORMAT_SHORT_YEAR = ['%a, %b %d']


def versatile_date_parse(date_str):
    if date_str is None:
        return None

    # Fixed bug multi language
    try:
        new_date_str = nomalize_date_str(date_str)
        dt = dateparser.parse(new_date_str)
        if dt:
            return dt
    except:
        pass

    date_str = date_str.encode('ascii', 'ignore')
    for date_format in ACCEPTED_FORMAT_FULL:
        try:
            dt = datetime.strptime(date_str, date_format)
            return dt
        except ValueError as e:
            pass
    # Missing year
    for date_format in ACCEPTED_FORMAT_SHORT_YEAR:
        try:
            dt = datetime.strptime(date_str, date_format)
            # add current year to string date and format date
            date_format = date_format + ', %Y'
            date_str = date_str + ', ' + str(datetime.now().year)
            dt = datetime.strptime(date_str, date_format)
            return dt
        except ValueError as e:
            pass

    logging.error("Error convert date_str: '%s'" % date_str)
    return None


def is_date(date_str, format='%Y-%m-%d'):
    try:
        date = datetime.strptime(date_str, format)
        return date
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def compare_date(date_str1, date_str2, format='%Y-%m-%d'):
    """
        Compare date

        :param date_str1:
            String date1
        :param date_str2:
            String date2
        :param format:
            https://docs.python.org/2/library/datetime.html
        :return:

    """
    date1 = is_date(date_str1, format)
    date2 = is_date(date_str2, format)
    if date1 < date2:
        return -1
    elif date1 > date2:
        return 1
    else:
        return 0


def replace_time(dt, time):
    return dt.replace(hour=time.hour, minute=time.minute,
                      second=time.second, microsecond=time.microsecond)


def convert_to_utc_tz(dt):
    return convert_to_tz(dt, pytz.UTC)


def convert_to_tz(dt, tz):
    try:
        return dt.astimezone(tz)
    except ValueError:
        try:
            return tz.localize(dt)
        except ValueError:
            return dt.replace(tzinfo=tz)


def utcnow():
    return pytz.UTC.localize(datetime.utcnow())


def now(zone='UTC'):
    now_utc = utcnow()
    tz = timezone(zone)
    return now_utc.astimezone(tz)


def next_date(dt, days=1):
    return dt + timedelta(days=days)


def prev_date(dt, days=1):
    return dt - timedelta(days=days)


def human_datetime(str_date):
    try:
        created_at = convert_to_utc_tz(parser.parse(str_date))
        return humanize.naturaltime(created_at)
    except:
        return None


def cal_delta(from_date, to_date=str(datetime.now())):
    try:
        time_from_date = parser.parse(from_date)
        time_to_date = parser.parse(to_date)
        return relativedelta.relativedelta(time_to_date, time_from_date)
    except Exception as e:
        logging.warn("cal_delta: %s" % e)
        return None


def human_date(str_date, format='%a %d %b, %Y'):
    try:
        dt = parser.parse(str_date)
        return dt.strftime(format)
    except:
        return str_date


def is_out_of_date(str_date, delta=7):
    try:
        dt = parser.parse(str_date).date()
        date_point = dt + timedelta(days=delta)
        current_date = now().date()
        return current_date > date_point
    except Exception as ex:
        logging.error(ex)
        return False
