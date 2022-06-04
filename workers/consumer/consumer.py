#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class Consumer:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write

    def start(self):
        # Wait for rabbitmq to come up
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
        connection.close()

    def callback(self, ch, method, properties, body):
        for queue in self.queues_to_write:
            if json.loads(body) == json.dumps({}):
                body = json.dumps({})
            ch.basic_publish(
                exchange='',
                routing_key=queue,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))



