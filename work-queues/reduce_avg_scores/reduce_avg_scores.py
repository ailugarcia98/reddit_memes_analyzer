#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class ReduceAvgScores:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.avg_score = 0

    def start(self):
        time.sleep(30)

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
        post = body.decode('utf-8')
        new_body = post.split(',')
        if int(new_body[1]) != 0:
            avg = int(new_body[0])/int(new_body[1])
            avg_encode = str(avg).encode('utf-8')
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=avg_encode,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))
        else:
            logging.error("Div 0 error")




