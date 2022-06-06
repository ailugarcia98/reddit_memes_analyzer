#!/usr/bin/env python3
import pika
import time
import json
import logging


class MapRemoveColumns5:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write

    def start(self):
        time.sleep(20)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_to_read, durable=True)
        for queue in self.queues_to_write:
            channel.queue_declare(queue=queue, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        body_recv = eval(body.decode('utf-8'))
        url = self.new_body(body_recv).encode('utf-8')
        for queue in self.queues_to_write:
            ch.basic_publish(
                exchange='',
                routing_key=queue,
                body=url,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

    def new_body(self, body):
        url = body[0]
        return f"{url}"


