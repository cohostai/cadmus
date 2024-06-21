#!/usr/bin/env python
# encoding: utf-8
"""
response

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import json

from flask import make_response as _make_response


def make_response(resp, status=200, mine_type='application/json', **kwargs):
    response = _make_response(json.dumps(resp), status)
    response.mimetype = mine_type
    return response


def file_too_large():
    return make_response({
        'error_code': 413,
        'error_message': 'File too large.'
    }, 413)


def no_file_provided():
    return make_response({
        'error_code': 400,
        'error_message': 'No file provided. Please choose a file.'
    }, 400)


def invalid_file_type():
    return make_response({
        'error_code': 400,
        'error_message': 'Invalid file type. Images are allowed only.'
    }, 400)


def invalid_token(e):
    return make_response({
        'error_code': 401,
        'error_message': str(e)
    }, 401)


def user_not_found(e):
    return make_response({
        'error_code': 404,
        'error_message': str(e)
    }, 404)


def internal_server_error(e):
    return make_response({
        'error_code': 500,
        'error_message': str(e)
    }, 500)
