#!/usr/bin/env python
# encoding: utf-8

from urllib.parse import urlparse


def file_name(url):
    result = urlparse(url)
    return result.path.split("/")[-1]
