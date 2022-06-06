#!/usr/bin/env python3
import pika
import time
import os
import logging
import json


class ReducePostID:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.dict_sentiment = []

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

    def callback(self, ch, method, properties, body):
        comments = eval(body.decode('utf-8'))
        new_body = str(self.new_body(comments)).encode('utf-8')
        for queue in self.queues_to_write:
            ch.basic_publish(
                exchange='',
                routing_key=queue,
                body=new_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

    def new_body(self, comments):
        new_body = []
        for comment in comments:
            url = comment[0]
            avg = float(comment[1]) / float(comment[2])
            new_body.append([url, avg])
        return new_body



