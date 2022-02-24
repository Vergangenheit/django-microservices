import json
import os
import django
from typing import Dict
from confluent_kafka import Consumer
from confluent_kafka.cimpl import Message
from django.core.mail import send_mail

from secrets.secrets import sasl_password


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

    consumer.subscribe(['email_topic'])

    while True:
        msg: Message = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        print("Message received is : {}".format(msg.value()))

        order: Dict = json.loads(msg.value())
        send_mail(
            subject='An Order has been completed',
            message='Order #' + str(order.get('id')) + 'with a total of $' + str(
                order.get('admin_revenue')) + ' has been completed!',
            from_email='from@email.com',
            recipient_list=['admin@admin.com']
        )

        send_mail(
            subject='An Order has been completed',
            message='You earned $' + str(order.get('ambassador_revenue')) + ' from the link #' + order.get('code'),
            from_email='from@email.com',
            recipient_list=[order.get('ambassador_email')]
        )
    consumer.close()


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    django.setup()
    main()
