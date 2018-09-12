#!/usr/bin/env python
# encoding: utf-8
"""
subscribe

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from kafka import KafkaConsumer
from kafka import KafkaProducer

from ..parser import email_parser
from ..parser.exceptions import DontParseEmailOTAError
from ..parser.exceptions import NotFoundOTASupportError
from ..utils.kafka.deserializers import JsonDeserializer
from ..utils.kafka.serializers import JsonSerializer

logger = logging.getLogger(__name__)


class RawEmailSubscribe(object):

    def __init__(self, bootstrap_servers, raw_email_topic, handled_email_topic, **kwargs):

        self._raw_email_topic = raw_email_topic
        self._handled_email_topic = handled_email_topic

        self._consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id='email-subscribe',
            value_deserializer=JsonDeserializer(),
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )

        self._consumer.subscribe([self._raw_email_topic])

        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            max_in_flight_requests_per_connection=1,
            retries=128,
            acks='all',
            value_serializer=JsonSerializer(),
            client_id='handled-email-client'
        )

    def raw_email_callback_error(self, email):
        # TODO(khoidn): Notify admin
        pass

    def handle(self):
        for record in self._consumer:
            try:
                logger.debug('EMAIL RECORD: %s', record)

                sendgrid_data = record.value
                handled_email = email_parser.parse(sendgrid_data)

                # Push to handled email topic
                future = self._producer.send(self._handled_email_topic, value=handled_email)
                future.add_callback().add_errback(self.raw_email_callback_error, email=record)

                self._consumer.commit()

            except (DontParseEmailOTAError, NotFoundOTASupportError, ):
                # TODO(khoidn): Notify admin
                pass
            except Exception as ex:
                logger.error("Handle raw email: %s" % ex, exc_info=True)

                self._consumer.close()
