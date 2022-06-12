#!/usr/bin/env python3
import json
import logging
import signal
import sys


class FilterBodyStudent:
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
        comments = json.loads(body.decode('utf-8'))
        send_array = []
        for comment in comments:
            if comment != str({}):
                comments_students = self.new_body(comment)
                if comments_students != str(""):
                    send_array.append(comments_students)
            else:
                send_array.append(str({}))
        if len(send_array) > 0:
            for queue in self.queues_to_write:
                self.middleware.publish(queue, json.dumps(send_array))
            logging.info(f"[FILTER BODY STUDENT] END")
        self.middleware.ack(method)

    def new_body(self, comment):
        comment_body = str(comment.split('$$,$$')[1])
        if comment_body.__contains__("university") or comment_body.__contains__("college") or comment_body.__contains__("student") \
                or comment_body.__contains__("teacher") or comment_body.__contains__("professor"):
            new_comment = f"{comment.split('$$,$$')[0]}$$,$${comment.split('$$,$$')[2]}$$,$${comment.split('$$,$$')[4]}"
        else:
            new_comment = ""
        return str(new_comment)


