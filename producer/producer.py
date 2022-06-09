#!/usr/bin/env python3
import logging
import csv
import json
import signal
import sys


class Producer:
    def __init__(self, post_queue_name, post_file, comments_queue_name, \
                 comments_file, size_send, queue_response_avg, queue_response_url, \
                 queue_response_meme, middleware):
        self.post_queue_name = post_queue_name
        self.comments_queue_name = comments_queue_name
        self.post_file = post_file
        self.comments_file = comments_file
        self.size_send = size_send  # how many records Producer can send at the same time
        self.queue_response_avg = queue_response_avg
        self.queue_response_url = queue_response_url
        self.queue_response_meme = queue_response_meme
        self.middleware = middleware
        # graceful quit
        # Define how to do when it will receive SIGTERM
        signal.signal(signal.SIGTERM, self.__need_to_stop)
        signal.signal(signal.SIGINT, self.__need_to_stop)

    def __need_to_stop(self, *args):
        self.middleware.shutdown()
        sys.exit(0)

    def start(self):
        self.send_posts()
        self.send_comments()
        self.recv()

    def send_posts(self):
        self.send(self.post_file, self.post_queue_name)

    def send_comments(self):
        self.send(self.comments_file, self.comments_queue_name)

    def send(self, file, queue_name):
        self.middleware.declare(queue_name)

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
                        self.middleware.publish(queue_name, message)
                        rows = []
                        lines = 0

            if len(rows) != 0:
                message = json.dumps(rows)
                self.middleware.publish(queue_name, message)

            # Send "end char"
            message = json.dumps({})
            self.middleware.publish(queue_name, message)

        except Exception as e:
            logging.error(e)

    def recv(self):
        self.middleware.declare(self.queue_response_avg)
        self.middleware.subscribe(self.queue_response_avg, self.callback_avg)

        self.middleware.declare(self.queue_response_url)
        self.middleware.subscribe(self.queue_response_url, self.callback_url)

        self.middleware.declare(self.queue_response_meme)
        self.middleware.subscribe(self.queue_response_meme, self.callback_meme)

        self.middleware.wait_for_messages()

    def callback_avg(self, ch, method, properties, body):
        if str(body.decode('utf-8')) != str({}):
            logging.info(f"#### [PRODUCER] Received avg {body.decode('utf-8')} ####")

    def callback_url(self, ch, method, properties, body):
        if str(body.decode('utf-8')) != str({}):
            logging.info(f"#### [PRODUCER] Received url {body.decode('utf-8')} ####")

    def callback_meme(self, ch, method, properties, body):
        meme_file = body
        open("/meme/meme_downloaded.jpg", "wb").write(meme_file)
        logging.info("#### [PRODUCER] Received meme ####")

