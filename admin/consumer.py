import json
import os
import django
from typing import Dict
from confluent_kafka import Consumer
from confluent_kafka.cimpl import Message
from secrets.secrets import sasl_password
import core.listeners
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from core.serializers import LinkSerializer


def main():
    consumer = Consumer({
        'bootstrap.servers': 'pkc-4r297.europe-west1.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.username': 'L2L7EQCZPLLFPF7X',
        'sasl.password': sasl_password,
        'sasl.mechanism': 'PLAIN',
        'group.id': 'myGroup',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(['admin_topic'])

    while True:
        msg: Message = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        getattr(core.listeners, msg.key().decode('utf-8'))(json.loads(msg.value()))

    consumer.close()


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    django.setup()
    main()
