import json
import os
import django
from confluent_kafka import Consumer
from confluent_kafka.cimpl import Message
from app.secrets import sasl_password

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

import core.listeners
from core.models import KafkaError


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

    consumer.subscribe(['ambassador_topic'])

    while True:
        msg: Message = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        try:
            getattr(core.listeners, msg.key().decode('utf-8'))(json.loads(msg.value()))
        except Exception as e:
            print(e)
            KafkaError.objects.create(
                key=msg.key(),
                value=msg.value(),
                error=e,
            )
    consumer.close()


if __name__ == '__main__':
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    # django.setup()
    main()
