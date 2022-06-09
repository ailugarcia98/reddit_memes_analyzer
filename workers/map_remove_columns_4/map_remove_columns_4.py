#!/usr/bin/env python3
import signal
import sys


class MapRemoveColumns4:
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

    def sentiment_not_null(self, comment):
        sentiment = str(comment.split(',')[3])
        return sentiment != str('')

    def callback(self, ch, method, properties, body):
        comments = eval(body.decode('utf-8'))
        for comment in comments:
            if comment != str({}) and self.sentiment_not_null(comment):
                new_body = self.new_body(comment).encode('utf-8')
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, new_body)
            else:
                if comment == str({}):
                    for queue in self.queues_to_write:
                        self.middleware.publish(queue, str({}))
                self.middleware.shutdown()

    def new_body(self, body):
        post_id = str(body.split('$$,$$')[0])
        sentiment = str(body.split('$$,$$')[3])
        url = str(body.split('$$,$$')[4])
        return f"{post_id}$$,$${sentiment}$$,$${url}"


