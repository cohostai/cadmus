#!/usr/bin/env python
# encoding: utf-8
"""
s3

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import uuid
from os import path

import boto3

from .config import AppConfig

s3 = boto3.client('s3')


def get_uuid():
    return str(uuid.uuid4())


def get_s3_key(filename, key_prefix):
    _, extension = path.splitext(filename)
    if extension:
        basename = get_uuid() + extension
    else:
        basename = filename

    return path.join(key_prefix, basename)


def upload_fileobj(fileobj,
                   key_prefix='images/',
                   acl="public-read"):
    try:
        key = get_s3_key(fileobj.filename, key_prefix)
        s3.upload_fileobj(
            fileobj,
            AppConfig.S3_BUCKET,
            key,
            ExtraArgs={
                "ACL": acl,
                "ContentType": fileobj.content_type
            }
        )

        return 'http://{}.s3.amazonaws.com/{}'.format(AppConfig.S3_BUCKET, key)
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        raise
