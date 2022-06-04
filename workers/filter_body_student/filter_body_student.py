#!/usr/bin/env python3
import pika
import time
import json
import logging

class FilterBodyStudent:
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
        comments = eval(body)
        for comment in comments:
            comments_students = self.new_body(comment)
            if comments_students != str(""):
                for queue in self.queues_to_write:
                    ch.basic_publish(
                        exchange='',
                        routing_key=queue,
                        body=comments_students,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                        ))

    def new_body(self, comment):
        comment_body = str(comment.split(',')[1])
        if comment_body.__contains__("university") or comment_body.__contains__("college") or comment_body.__contains__("student") \
                or comment_body.__contains__("teacher") or comment_body.__contains__("professor"):
            new_comment = f"{comment.split(', ')[0]}, {comment.split(', ')[2]}, {comment.split(', ')[4]}"
        else:
            new_comment = ""
        return str(new_comment)


