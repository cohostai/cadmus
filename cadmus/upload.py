#!/usr/bin/env python
# encoding: utf-8
"""
images

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from os import path

from flask import Flask
from flask import jsonify
from flask import request
from jose import JWTError
from werkzeug.utils import secure_filename

from . import response
from . import s3
from .auth import Auth
from .auth import NotFoundError
from .config import AppConfig

ALLOWED_EXTENSIONS = [
    ".jpg",
    ".jpe",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".bmp"
]

auth = Auth(
    issuer='https://%s/' % AppConfig.AUTH0_AUTH_DOMAIN,
    api_audience=AppConfig.COHOST_API_AUDIENCE,
    jwks_url=AppConfig.COHOST_JWKS_URL
)

app = Flask(__name__)
app.config.from_object(AppConfig)


def allowed_file(fileobj):
    name, extension = path.splitext(fileobj.filename)
    return extension and extension.lower() in ALLOWED_EXTENSIONS


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
def upload_user_images():
    if "file" not in request.files:
        return response.no_file_provided()

    fileobj = request.files["file"]
    if not fileobj.filename:
        return response.no_file_provided()

    if not allowed_file(fileobj):
        return response.invalid_file_type()

    fileobj.filename = secure_filename(fileobj.filename)
    key_prefix = "pictures/user"
    url = s3.upload_fileobj(fileobj, key_prefix=key_prefix)

    return jsonify({
        "url": url
    })


@app.route('/pictures/message', methods=['POST'])
@auth.require_auth
def upload_message_image():
    if "file" not in request.files:
        return response.no_file_provided()

    fileobj = request.files["file"]
    if not fileobj.filename:
        return response.no_file_provided()

    if not allowed_file(fileobj):
        return response.invalid_file_type()

    fileobj.filename = secure_filename(fileobj.filename)
    key_prefix = "pictures/message"
    url = s3.upload_fileobj(fileobj, key_prefix=key_prefix)

    return jsonify({
        "url": url
    })


@app.route('/upload/health_check', methods=['GET'])
def health_check():
    return jsonify({
        "message": "I am still ok"
    })


if __name__ == '__main__':
    app.run('0.0.0.0', 8008, debug=True)
