#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class FilterScoreMayorAvg:
    def __init__(self, queue_to_read_avg, queue_to_read_filter, queues_to_write):
        self.queue_to_read_avg = queue_to_read_avg
        self.queue_to_read_filter = queue_to_read_filter
        self.queues_to_write = queues_to_write
        self.avg = 0.0

    def start(self):
        # Wait for rabbitmq to come up
        time.sleep(20)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        for queue in self.queues_to_write:
            channel.queue_declare(queue=queue, durable=True)

        channel.queue_declare(queue=self.queue_to_read_avg, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read_avg, on_message_callback=self.callback_avg, auto_ack=True)

        channel.queue_declare(queue=self.queue_to_read_filter, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read_filter, on_message_callback=self.callback_filter, auto_ack=True)
        channel.start_consuming()

        connection.close()

    def callback_filter(self, ch, method, properties, body):
        score_body = float(body.decode('utf-8').split(',')[1])
        if score_body > self.avg:
            url = str(body.decode('utf-8').split(',')[2])
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=url.encode('utf-8'),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))


    def callback_avg(self, ch, method, properties, body):
        self.avg = float(eval(body.decode('utf-8')))




