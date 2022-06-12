#!/usr/bin/env python3
import json
import logging
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
        sentiment = str(comment.split('$$,$$')[3])
        return sentiment != str('')

    def url_not_null(self, comment):
        url = str(comment.split('$$,$$')[4])
        return url != str('')

    def callback(self, ch, method, properties, body):
        comments = json.loads(body.decode('utf-8'))
        send_array = []
        for comment in comments:
            if comment != str({}) and self.sentiment_not_null(comment) and \
                    self.url_not_null(comment):
                new_body = self.new_body(comment)
                send_array.append(new_body)
            else:
                if comment == str({}):
                    send_array.append(str({}))
        if len(send_array) > 0:
            for queue in self.queues_to_write:
                self.middleware.publish(queue, json.dumps(send_array))
        logging.info(f"[MRC4] END")
        self.middleware.ack(method)

    def new_body(self, body):
        post_id = str(body.split('$$,$$')[0])
        sentiment = str(body.split('$$,$$')[3])
        url = str(body.split('$$,$$')[4])
        return f"{post_id}$$,$${sentiment}$$,$${url}"


