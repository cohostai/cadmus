#!/usr/bin/env python
# encoding: utf-8
"""
serializers

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

import json

from kafka.serializer import Serializer


class JsonSerializer(Serializer):

    def serialize(self, topic, value):
        json_str = json.dumps(value, ensure_ascii=False)
        return json_str.encode('utf-8')


class MessagePackSerializer(Serializer):

    def serialize(self, topic, value):
        raise NotImplementedError
