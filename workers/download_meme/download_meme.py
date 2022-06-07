#!/usr/bin/env python3
import pika
import time
import requests
import logging
import json


class DownloadMeme:
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

    def callback(self, ch, method, properties, body):
        meme_to_download = body.decode('utf-8')
        meme_downloaded = self.download_meme(meme_to_download)
        if meme_downloaded is not None:
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=meme_downloaded,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

    def download_meme(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            meme = response.content
        else:
            meme = None
        return meme
