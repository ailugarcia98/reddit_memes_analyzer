#!/usr/bin/env python3
import logging
import signal
import sys


class FindMaxSentAvg:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.dict_sentiment = []
        self.max_avg = 0.0
        self.url_max_avg = ''
        self.middleware = middleware
        # graceful quit
        # Define how to do when it will receive SIGTERM
        signal.signal(signal.SIGTERM, self.__need_to_stop)
        signal.signal(signal.SIGINT, self.__need_to_stop)

    def __need_to_stop(self, *args):
        self.middleware.shutdown()
        sys.exit(0)

    def start(self):

        self.middleware.declare(self.queue_to_read)
        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.subscribe(self.queue_to_read, self.callback)

        self.middleware.wait_for_messages()

    def callback(self, ch, method, properties, body):
        comments = eval(body.decode('utf-8'))
        if str(body.decode('utf-8')) != str({}):
            new_body = str(self.new_body(comments)).encode('utf-8')
            for queue in self.queues_to_write:
                self.middleware.publish(queue, new_body)
            self.middleware.ack(method)
        else:
            for queue in self.queues_to_write:
                self.middleware.publish(queue, str({}).encode('utf-8'))
            self.middleware.ack(method)
            logging.info(f"[FIND MAX SENT AVG] END")
            self.middleware.shutdown()

    def new_body(self, comments):
        for comment in comments:
            url = comment[0]
            avg = float(comment[1])
            if self.max_avg < avg:
                self.max_avg = avg
                self.url_max_avg = url
        return [self.url_max_avg, self.max_avg]



