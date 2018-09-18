#!/usr/bin/env python
# encoding: utf-8

import logging
import re
from lxml import html

logger = logging.getLogger(__name__)


class HtmlEmailParserBase(object):
    def __init__(self, required, optional=None, newline_fields=None):
        self.required_xpaths = required
        self.optional_xpaths = optional or {}
        self.newline_fields = newline_fields or []

    def parse_field(self, field, value):
        if field in self.newline_fields:
            return self.parse_newline_field(value)

        if hasattr(value, 'text_content'):
            value = value.text_content()
        return value

    @staticmethod
    def parse_newline_field(value):
        newline_tags = ["p", "br"]

        for tag in newline_tags:
            t_xpath = ".//%s" % tag
            if hasattr(value, 'xpath'):
                for el in value.xpath(t_xpath):
                    if tag != "br":
                        el.text = "\n" + el.text if el.text else "\n"

                    el.tail = "\n" + el.tail if el.tail else "\n"

        if hasattr(value, 'text_content'):
            result = value.text_content()
            return result.strip() if result else ''

        return value

    def parse(self, sendgrid_data):
        logging.debug(self.__class__.__name__)
        tree = html.fromstring(sendgrid_data['html'])

        parsed = {}
        for field, xpath in self.required_xpaths.items():
            value = tree.xpath(xpath)
            logging.debug("extract %s => %s", field, value)
            if not value:
                logging.debug("Missing value with %s field", field)
                return None

            # if field is feedback, it will have values
            if field == 'feedback':
                parsed.update({field: value})
                continue

            if len(value) > 1:
                logging.warning("Too many results for xpath\
                                 query for field %s", field)

            value = value[0]
            value = self.parse_field(field, value)

            if not value:
                logging.debug("Missing value with %s field and\
                                 attr text_content", field)
                return None

            parsed.update({field: re.sub(r"[ \t]+", ' ', value.strip())})

        for field, xpath in self.optional_xpaths.items():
            value = tree.xpath(xpath)
            if not value:
                parsed.update({field: value})
                continue
            value = value[0]
            value = self.parse_field(field, value)
            parsed.update({field: value.strip()})

        return parsed


class CascadingEmailParser(object):
    """
    Walk through the list of handlers, the first one succeeds will be the answer.
    """
    def __init__(self, parsers):
        self._parsers = parsers

    def parse(self, sendgrid_data):
        for parser in self._parsers:
            res = parser.parse(sendgrid_data)
            if res:
                return res
        return None
