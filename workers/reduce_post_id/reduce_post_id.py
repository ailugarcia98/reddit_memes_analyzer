#!/usr/bin/env python3
import signal


class ReducePostID:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.dict_sentiment = []
        self.middleware = middleware
        # graceful quit
        # Define how to do when it will receive SIGTERM
        signal.signal(signal.SIGTERM, self.__need_to_stop)
        signal.signal(signal.SIGINT, self.__need_to_stop)

    def __need_to_stop(self, *args):
        self.middleware.shutdown()

    def start(self):

        self.middleware.declare(self.queue_to_read)
        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.subscribe(self.queue_to_read, self.callback)
        self.middleware.wait_for_messages()

    def callback(self, ch, method, properties, body):
        comments = eval(body.decode('utf-8'))
        new_body = str(self.new_body(comments)).encode('utf-8')
        for queue in self.queues_to_write:
            self.middleware.publish(queue, new_body)

    def new_body(self, comments):
        new_body = []
        for comment in comments:
            url = comment[0]
            avg = float(comment[1]) / float(comment[2])
            new_body.append([url, avg])
        return new_body



