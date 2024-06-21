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
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image
import boto3

from .config import AppConfig

IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpe",
    ".jpeg",
    ".png",
]

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


def upload_fileobj(fileobj, key_prefix='images/'):
    try:
        key = get_s3_key(fileobj.filename, key_prefix)

        extra_args = {
            "ContentType": fileobj.content_type
        }

        # check image format
        if path.splitext(fileobj.filename)[1] in IMAGE_EXTENSIONS:
            # Open the image using Pillow
            image = Image.open(fileobj.stream)
            width, height = image.size
            # Save the image to a BytesIO object
            image_bytes = BytesIO()
            image.save(image_bytes, format=image.format)
            image_bytes.seek(0)
            # Upload the image to S3
            s3.upload_fileobj(image_bytes,AppConfig.S3_BUCKET,key,ExtraArgs=extra_args)
        else:
            # If the file is not an image, set the width and height to 0
            width, height = 0, 0
            # Upload the file to S3
            s3.upload_fileobj(fileobj,AppConfig.S3_BUCKET,key,ExtraArgs=extra_args)
            
        return urljoin(AppConfig.BASE_URL, key), width, height
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        raise
