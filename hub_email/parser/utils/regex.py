#!/usr/bin/env python
# encoding: utf-8
"""
regex

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re


def extract_from_regex(content, regex, group_id=0):
    try:
        return re.search(regex, content).group(group_id).strip()
    except Exception:
        return None
