#!/usr/bin/env python3
import signal
import sys


class MapRemoveColumns5:
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
        body_recv = eval(body.decode('utf-8'))
        if str(body.decode('utf-8')) != str({}):
            url = self.new_body(body_recv).encode('utf-8')
            for queue in self.queues_to_write:
                self.middleware.publish(queue, url)
            self.middleware.ack(method)
        else:
            for queue in self.queues_to_write:
                self.middleware.publish(queue, str({}).encode('utf-8'))
            logging.info(f"[MRC5] END")
            self.middleware.ack(method)
            self.middleware.shutdown()

    def new_body(self, body):
        url = body[0]
        return f"{url}"


