#!/usr/bin/env python3
import json
import logging
import signal
import sys


class Consumer:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
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
        for queue in self.queues_to_write:
            if str(body) == str({}):
                body = json.dumps({})
                self.middleware.publish(queue, body)
                logging.info(f"[CONSUMER] END")
            else:
                self.middleware.publish(queue, body)
        self.middleware.ack(method)

