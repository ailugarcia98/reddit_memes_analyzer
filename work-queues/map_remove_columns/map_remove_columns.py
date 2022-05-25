#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class MapRemoveColumns:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write

    def start(self):
        logging.debug(f"[MAP REMOVE COLUMNS] sleep")
        time.sleep(30)
        logging.debug(f"[MAP REMOVE COLUMNS] wake up")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_to_read, durable=True)
        for queue in self.queues_to_write:
            channel.queue_declare(queue=queue, durable=True)
            logging.debug(f"[MAP REMOVE COLUMNS] create queue {queue}")

        logging.debug(f"[MAP REMOVE COLUMNS] sali del for")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        logging.debug(f"[MAP REMOVE COLUMNS] call back")
        posts = json.loads(body)
        for post in posts:
            logging.debug(f"[MAP REMOVE COLUMNS] for")
            new_body = self.new_body(post)
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=new_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

    def new_body(self, body):
        logging.debug(f"[MAP REMOVE COLUMNS] {body['id'], body['score']}")
        return b'(body["id"], body["score"])'


