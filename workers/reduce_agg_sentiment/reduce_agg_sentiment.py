#!/usr/bin/env python3
import pika
import time
import os
import logging
import json

class ReduceAggSentiment:
    def __init__(self, queue_to_read, queues_to_write):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.dict_sentiment = []

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
        comment = body.decode('utf-8')
        if comment == str({}):
            new_body = json.dumps(self.agg()).encode('utf-8')
            logging.info(f"[REDUCE] {new_body}")
            for queue in self.queues_to_write:
                ch.basic_publish(
                    exchange='',
                    routing_key=queue,
                    body=new_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))
        else:
            self.new_body(comment)

    def new_body(self, comment):
        maybe_sentiment = comment.split(',')[1]
        logging.info(f"MAYBE SENTIMENT {maybe_sentiment}")
        if maybe_sentiment != str(''):
            sentiment = float(comment.split(',')[1])
            post_id = comment.split(',')[0]
            url = comment.split(',')[2]
            self.dict_sentiment.append((post_id,url,sentiment,int(1)))

    def agg(self):
        old_body = {}
        for post_id, url, sentiment, count in self.dict_sentiment:
            try:
                prev_sentiment, prev_count = old_body[url]
            except KeyError:
                old_body[url] = float(sentiment), int(count)
            else:
                new_sentiment = float(sentiment) + float(prev_sentiment)
                new_count = int(prev_count) + int(count)
                old_body[url] = new_sentiment, new_count
        return old_body


