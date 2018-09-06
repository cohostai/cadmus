#!/usr/bin/env python
# encoding: utf-8
"""
deserializers

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from kafka.serializer import Deserializer

import json


class JsonDeserializer(Deserializer):

    def deserialize(self, topic, bytes_):
        message = bytes_.decode('utf-8')
        return json.loads(message)
