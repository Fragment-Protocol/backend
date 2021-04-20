import json
import os
import sys
import threading
import traceback

import pika

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()
from backend.locked_nft.api import create_locked_nft, create_bep20

from django.conf import settings


class Receiver(threading.Thread):

    def __init__(self, queue):
        super().__init__()
        self.network = queue

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq',
            5672,
            'rabbit',
            pika.PlainCredentials('rabbit', 'rabbit'),
        ))

        channel = connection.channel()
        queue_name = settings.NETWORK_SETTINGS[self.network]['queue']
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            auto_delete=False,
            exclusive=False
        )
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.callback
        )

        print(
            'RECEIVER MAIN: started on {net} with queue `{queue_name}`'
                .format(net=self.network, queue_name=queue_name)
        )

        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print('received', body, properties, method)
        try:
            message = json.loads(body.decode())
            if message.get('status', '') == 'COMMITTED':
                getattr(self, properties.type, self.unknown_handler)(message)
        except Exception as e:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def unknown_handler(self, message):
        print('unknown message', message)

    def deposit_nft(self, message):
        create_locked_nft(message)

    def token_created(self, message):
        create_bep20(message)


if __name__ == '__main__':
    for network in settings.NETWORK_SETTINGS.keys():
        receiver = Receiver(network)
        receiver.start()
