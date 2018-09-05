#!/usr/bin/env python
# encoding: utf-8
"""
main

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from elasticsearch import Elasticsearch
from kafka import KafkaConsumer

from integrations.indexer import config
from integrations.indexer.creator import CompositeIndexCreator
from integrations.indexer.creator import UsersIndexCreator
from integrations.indexer.creator.user import INDEX_NAME as users_index
from integrations.indexer.indexer import Indexer
from integrations.indexer.processor import CascadingRowProcessor
from integrations.indexer.processor import UserRowProcessor
from integrations.indexer.utils.kafka.deserializers import JsonDeserializer
from integrations.indexer.utils import log

logger = log.get_logger(__name__)


def get_stream():
    # TODO(thuync): Read more about kafka consumer options and transaction
    stream = KafkaConsumer(
        config.KAFKA_EVENT_TOPIC,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=config.KAFKA_CONSUMER_GROUP,
        value_deserializer=JsonDeserializer(),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

    return stream


def get_es_client():
    return Elasticsearch(config.ELASTICSEARCH_HOSTS)


def get_index_creator(es_client):
    index_creator = CompositeIndexCreator(
        creators=[
            UsersIndexCreator(es_client)
        ]
    )

    return index_creator


def get_row_processor():
    row_processor = CascadingRowProcessor()
    row_processor.register('chocon', 'user', UserRowProcessor())

    return row_processor


def main():
    stream = get_stream()

    es_client = get_es_client()

    index_creator = get_index_creator(es_client)
    row_processor = get_row_processor()
    table_to_index = {
        'chocon.user': users_index
    }

    indexer = Indexer(
        es_client,
        table_to_index,
        index_creator,
        row_processor
    )

    batch = []
    for record in stream:
        try:
            logger.debug('NEW RECORD: %s', record)
            event = record.value
            batch.append(event)
            if len(batch) >= config.BATCH_SIZE:
                indexer.process(batch)
                stream.commit()
                batch = []
        except:
            stream.close()
            raise


if __name__ == "__main__":
    main()
