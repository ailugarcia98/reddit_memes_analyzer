#!/usr/bin/env python3
import pika
import logging
import time
import csv
import json

class Producer:
    def __init__(self, post_queue_name, post_file, comments_queue_name, \
                 comments_file, size_send, queue_response):
        self.post_queue_name = post_queue_name
        self.comments_queue_name = comments_queue_name
        self.post_file = post_file
        self.comments_file = comments_file
        self.size_send = size_send #how many records Producer can send at the same time
        self.queue_response = queue_response

    def start(self):
        # Wait for rabbitmq to come up
        time.sleep(50)
        self.send_posts()
        self.send_comments()
        self.recv()

    def send_posts(self):
        self.send(self.post_file, self.post_queue_name)

    def send_comments(self):
        self.send(self.comments_file, self.comments_queue_name)

    def send(self, file, queue_name):
        # Create RabbitMQ communication channel
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        try:
            with open(file, mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                lines = 0
                rows = []
                for row in reader:
                    rows.append(row)
                    lines += 1
                    if lines == self.size_send:
                        message = json.dumps(rows)
                        channel.basic_publish(
                            exchange='',
                            routing_key=queue_name,
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))
                        rows = []
                        lines = 0

            if len(rows) != 0:
                message = json.dumps(rows)
                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

            #Send "end char"
            message = json.dumps({})
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            connection.close()

        except Exception as e:
            logging.error(e)

    def recv(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_response, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_response, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()
        connection.close()

    def callback(self, ch, method, properties, body):
        logging.info(f"[PRODUCER] Received avg {body.decode('utf-8')}")
