#!/usr/bin/env python3
import json
import logging
import signal
import sys


class FilterScoreMayorAvg:
    def __init__(self, queue_to_read_avg, queue_to_read_filter, queues_to_write, middleware):
        self.queue_to_read_avg = queue_to_read_avg
        self.queue_to_read_filter = queue_to_read_filter
        self.queues_to_write = queues_to_write
        self.avg = None
        self.urls = []
        self.end_post = False
        self.have_avg = False
        self.posts_before_avg_arrived = []
        self.middleware = middleware
        # graceful quit
        # Define how to do when it will receive SIGTERM
        signal.signal(signal.SIGTERM, self.__need_to_stop)
        signal.signal(signal.SIGINT, self.__need_to_stop)

    def __need_to_stop(self, *args):
        self.middleware.shutdown()
        sys.exit(0)

    def start(self):

        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.declare(self.queue_to_read_avg)
        self.middleware.subscribe(self.queue_to_read_avg, self.callback_avg)

        self.middleware.declare(self.queue_to_read_filter)
        self.middleware.subscribe(self.queue_to_read_filter, self.callback_filter)

        self.middleware.wait_for_messages()

    def callback_filter(self, ch, method, properties, body):
        recv = json.loads(body)
        for i in recv:
            if i != str({}):
                score_body = float(i.split('$$,$$')[1])
                if self.avg is None:
                    self.posts_before_avg_arrived.append(i)
                else:
                    if score_body > self.avg:
                        url = str(i.split('$$,$$')[2])
                        if url not in self.urls:
                            self.urls.append(url)
            else:
                self.end_post = True
                if self.end_post and self.have_avg:
                    self.send_final_posts(method)
                else:
                    self.middleware.ack(method)

    def callback_avg(self, ch, method, properties, body):
        self.avg = float(eval(body.decode('utf-8')))
        logging.info(f"avg {self.avg}")
        self.have_avg = True
        if self.end_post and self.have_avg:
            self.send_final_posts(method)
        else:
            self.middleware.ack(method)

    def send_final_posts(self, method):
        for post in self.posts_before_avg_arrived:
            score_body = float(post.split('$$,$$')[1])
            if score_body > self.avg:
                url = str(post.split('$$,$$')[2])
                if url not in self.urls:
                    self.urls.append(url)
        for queue in self.queues_to_write:
            self.middleware.publish(queue, str(self.urls).encode('utf-8'))
        logging.info(f"[FILTER SCORE MAYOR AVG] END")
        self.middleware.ack(method)
        self.middleware.shutdown()






