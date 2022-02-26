from confluent_kafka import Producer
from .secrets import sasl_password

producer = Producer({
    'bootstrap.servers': 'pkc-4r297.europe-west1.gcp.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'L2L7EQCZPLLFPF7X',
    'sasl.password': sasl_password,
    'sasl.mechanism': 'PLAIN',
})

