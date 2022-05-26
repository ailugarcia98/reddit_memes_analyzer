#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class ReduceAggScores:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.count_posts = 0
        self.sum_score = 0

    def start(self):
        logging.debug(f"[REDUCE AGG SCORES] sleep")
        time.sleep(30)
        logging.debug(f"[REDUCE AGG SCORES] wake up")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_to_read, durable=True)
        for queue in self.queues_to_write:
            channel.queue_declare(queue=queue, durable=True)
            logging.debug(f"[REDUCE AGG SCORES] create queue {queue}")

        logging.debug(f"[REDUCE AGG SCORES] sali del for")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        logging.debug(f"[REDUCE AGG SCORES] call back")
        post = body.decode('utf-8')
        logging.debug(f"[REDUCE AGG SCORES] Received {post}")
        if post == '{}':
            new_body = self.new_body()
            logging.debug(f"[REDUCE AGG SCORES] Sending {new_body}")
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=new_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))
        else:
            self.count_posts += 1
            logging.debug(f"[REDUCE AGG SCORES] Split {post.split(',')}")
            self.sum_score += int(post.split(',')[1])

    def new_body(self):
        return f'{self.sum_score}, {self.count_posts}'



