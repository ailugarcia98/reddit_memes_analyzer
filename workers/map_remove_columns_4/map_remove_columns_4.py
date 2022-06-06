#!/usr/bin/env python3
import pika
import time
import json
import logging


class MapRemoveColumns4:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write

    def start(self):

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_to_read, durable=True)
        for queue in self.queues_to_write:
            channel.queue_declare(queue=queue, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()

    def sentiment_not_null(self, comment):
        sentiment = str(comment.split(',')[3])
        return sentiment != str('')

    def callback(self, ch, method, properties, body):
        comments = eval(body.decode('utf-8'))
        for comment in comments:
            if comment != str({}) and self.sentiment_not_null(comment):
                new_body = self.new_body(comment).encode('utf-8')
                for queue in self.queues_to_write:
                    ch.basic_publish(
                        exchange='',
                        routing_key=queue,
                        body=new_body,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                        ))
            else:
                if comment == str({}):
                    for queue in self.queues_to_write:
                        ch.basic_publish(
                            exchange='',
                            routing_key=queue,
                            body=str({}),
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))

    def new_body(self, body):
        post_id = str(body.split(',')[0])
        sentiment = str(body.split(',')[3])
        url = str(body.split(',')[4])
        return f"{post_id},{sentiment},{url}"


