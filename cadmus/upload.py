#!/usr/bin/env python
# encoding: utf-8
"""
images

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from os import path
from io import BytesIO

from flask import Flask
from flask import jsonify
from flask import request
from jose import JWTError
from flask_cors import CORS
from werkzeug.utils import secure_filename

import requests

from . import response
from . import s3
from .auth import Auth
from .auth import NotFoundError
from .config import AppConfig
from .utils import urls


ALLOWED_EXTENSIONS = [
    ".jpg",
    ".jpe",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".bmp",
    ".txt",
    ".pdf",
    ".doc"
]


auth = Auth(
    issuer='https://%s/' % AppConfig.AUTH0_AUTH_DOMAIN,
    api_audience=AppConfig.COHOST_API_AUDIENCE,
    jwks_url=AppConfig.COHOST_JWKS_URL
)

app = Flask(__name__)

CORS(app)

app.config.from_object(AppConfig)


def allowed_file(fileobj):
    name, extension = path.splitext(fileobj.filename)
    return extension and extension.lower() in ALLOWED_EXTENSIONS


def allowed_content_type(content_type):
    return content_type and content_type.lower().startswith("image")


@app.errorhandler(413)
def file_too_large(e):
    return response.file_too_large()


@app.errorhandler(JWTError)
def invalid_token(e):
    return response.invalid_token(e)


@app.errorhandler(NotFoundError)
def not_found_user(e):
    return response.user_not_found(e)


# TODO: make streaming upload
# TODO: validate client id
@app.route('/upload/user', methods=['POST'])
# @auth.require_auth
def upload_old_user_image():
    return upload_user_image()


@app.route('/pictures/user', methods=['POST'])
# @auth.require_auth
def upload_user_image():
    return _handle_upload("pictures/user")


@app.route('/pictures/message', methods=['POST'])
@auth.require_auth
def upload_message_image():
    return _handle_upload("pictures/message")


@app.route('/pictures/url', methods=['POST'])
def upload_image_from_url():
    body = request.get_json(force=True)
    resp = requests.get(body['url'])

    image_file = BytesIO(resp.content)
    image_file.filename = urls.file_name(body['url'])
    image_file.content_type = resp.headers.get('Content-Type')

    if not allowed_content_type(image_file.content_type):
        return response.invalid_file_type()

    key_prefix = "pictures/url"
    if request.args.get('type') == 'message':
        key_prefix = "pictures/message"

    url = s3.upload_fileobj(image_file, key_prefix=key_prefix)

    return jsonify({
        'url': url,
        'mimetype': resp.headers.get('Content-Type'),
    })


@app.route('/pictures/team', methods=['POST'])
@auth.require_auth
def upload_team_image():
    return _handle_upload("pictures/team")


@app.route('/pictures/listing', methods=['POST'])
@auth.require_auth
def upload_listing_image():
    return _handle_upload("pictures/listing")


@app.route('/pictures/attachments', methods=['POST'])
@auth.require_auth
def upload_attachments():
    return _handle_upload("pictures/attachments")


def _handle_upload(key_prefix):

    if "file" not in request.files:
        return response.no_file_provided()

    fileobj = request.files["file"]
    if not fileobj.filename:
        return response.no_file_provided()

    if not allowed_file(fileobj):
        return response.invalid_file_type()

    fileobj.filename = secure_filename(fileobj.filename)
    url = s3.upload_fileobj(fileobj, key_prefix=key_prefix)

    return jsonify({
        "url": url,
        "mimetype": fileobj.content_type
    })


@app.route('/upload/health_check', methods=['GET'])
def health_check():
    return jsonify({
        "message": "I am still ok"
    })


if __name__ == '__main__':
    app.run('0.0.0.0', 8008, debug=True)
