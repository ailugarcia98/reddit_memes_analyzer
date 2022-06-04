#!/usr/bin/env python3
import pika
import time
import json
import logging

class FilterDeletedRemoved:
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
        comments = json.loads(body)
        if comments == {}:
            new_body = json.dumps({})
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                routing_key=queue,
                body=new_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
        else:
            for comment in comments:
                comments_not_deleted_removed = self.new_body(comment)
                if comments_not_deleted_removed != json.dumps("removed/deleted"):
                    for queue in self.queues_to_write:
                        ch.basic_publish(
                            exchange='',
                            routing_key=queue,
                            body=comments_not_deleted_removed,
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))

    def new_body(self, comment):
        if comment["body"]=="[removed]" or comment["body"]=="[deleted]":
            new_comment = "removed/deleted"
        else:
            new_comment = comment
        return json.dumps(new_comment)


