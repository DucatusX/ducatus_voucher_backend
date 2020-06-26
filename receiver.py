import pika
import os
import traceback
import json
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ducatus_voucher.settings')
import django

django.setup()

from ducatus_voucher.settings import NETWORK_SETTINGS
from ducatus_voucher.transfers.api import confirm_transfer


class Receiver:

    def __init__(self, queue):
        super().__init__()
        self.network = queue

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'localhost',
            5672,
            'duc_voucher',
            pika.PlainCredentials('duc_voucher', 'duc_voucher'),
        ))

        channel = connection.channel()

        queue_name = NETWORK_SETTINGS[self.network]['queue']

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
                .format(net=self.network, queue_name=queue_name), flush=True
        )

        channel.start_consuming()

    def duc_transfer(self, message):
        print('PAYMENT MESSAGE RECEIVED', flush=True)
        confirm_transfer(message)

    def callback(self, ch, method, properties, body):
        print('received', body, properties, method, flush=True)
        try:
            message = json.loads(body.decode())
            if message.get('status', '') == 'COMMITTED':
                getattr(self, properties.type, self.unknown_handler)(message)
        except Exception as e:
            print('\n'.join(traceback.format_exception(*sys.exc_info())),
                  flush=True)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def unknown_handler(self, message):
        print('unknown message', message, flush=True)


if __name__ == '__main__':
    rec = Receiver('DUC')
    rec.run()
