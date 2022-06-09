#!/usr/bin/env python3
import logging
import signal
import sys


class ReduceAvgScores:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.avg_score = 0
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
        if str(post) != str({}):
            new_body = post.split(',')
            if int(new_body[1]) != 0:
                avg = int(new_body[0])/int(new_body[1])
                avg_encode = str(avg).encode('utf-8')
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, avg_encode)
            else:
                logging.error("Div 0 error")
        else:
            for queue in self.queues_to_write:
                self.middleware.publish(queue, str({}).encode('utf-8'))
            self.middleware.shutdown()




