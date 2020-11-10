#!/usr/bin/env python
# encoding: utf-8

from six.moves.urllib.parse import urlparse


def file_name(url):
    result = urlparse(url)
    return result.path.split("/")[-1]
