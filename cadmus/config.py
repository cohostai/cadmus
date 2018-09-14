#!/usr/bin/env python
# encoding: utf-8
"""
config

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from .utils.params import params_store
from .utils.text import to_int

params = params_store.get_params()


class AppConfig(object):
    SECRET_KEY = params['FLASK_SECRET_KEY']
    S3_BUCKET = params['UPLOAD_S3_BUCKET']
    MAX_CONTENT_LENGTH = to_int(params['UPLOAD_MAX_CONTENT_LENGTH'])
