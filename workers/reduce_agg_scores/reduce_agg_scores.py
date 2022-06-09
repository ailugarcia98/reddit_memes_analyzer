#!/usr/bin/env python3
import signal
import sys


class ReduceAggScores:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.count_posts = 0
        self.sum_score = 0
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
        post = body.decode('utf-8')
        if post == '{}':
            new_body = self.new_body()
            for queue in self.queues_to_write:
                self.middleware.publish(queue, new_body)
            self.middleware.shutdown()
        else:
            self.count_posts += 1
            self.sum_score += int(post.split(',')[1])

    def new_body(self):
        return f'{self.sum_score}, {self.count_posts}'




