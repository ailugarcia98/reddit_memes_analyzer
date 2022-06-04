#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class Join:
    def __init__(self, queue_to_read_2, queue_to_read_3, queues_to_write):
        self.queue_to_read_comments = queue_to_read_2
        self.queue_to_read_posts = queue_to_read_3
        self.queues_to_write = queues_to_write
        self.posts = []
        self.comments = []

    def start(self):
        # Wait for rabbitmq to come up
        time.sleep(20)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        for queue in self.queues_to_write:
            channel.queue_declare(queue=queue, durable=True)

        channel.queue_declare(queue=self.queue_to_read_posts, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read_posts, on_message_callback=self.callback_post, auto_ack=True)

        channel.queue_declare(queue=self.queue_to_read_comments, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_to_read_comments, on_message_callback=self.callback_comments, auto_ack=True)
        channel.start_consuming()

        connection.close()

    def callback_post(self, ch, method, properties, body):
        if body.decode('utf-8') != {}:
            self.posts.append(body.decode('utf-8'))

    def callback_comments(self, ch, method, properties, body):
        if body.decode('utf-8') != {}:
            self.comments.append(body.decode('utf-8'))

        new_body = []

        for post in self.posts:
            if str(post) != str({}):
                post_id = post.split(',')[0]
                for comment in self.comments:
                    comment_post_id = comment.split(',')[0]
                    if post_id == comment_post_id:
                        post_url = post.split(',')[1]
                        new_body.append(f'{comment}, {post_url}')
            else:
                queue = "queue_map_remove_columns_4"
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=str({}).encode('utf-8'),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

        for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=str(new_body).encode('utf-8'),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))



