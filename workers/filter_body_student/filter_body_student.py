#!/usr/bin/env python3
import signal
import logging


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

    def start(self):

        self.middleware.declare(self.queue_to_read)
        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.subscribe(self.queue_to_read, self.callback)

        self.middleware.wait_for_messages()

    def callback(self, ch, method, properties, body):
        comments = eval(body)
        for comment in comments:
            if comment != str({}):
                comments_students = self.new_body(comment)
                if comments_students != str(""):
                    for queue in self.queues_to_write:
                        self.middleware.publish(queue, comments_students)
            else:
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, str({}).encode('utf-8'))

    def new_body(self, comment):
        comment_body = str(comment.split('$$,$$')[1])
        if comment_body.__contains__("university") or comment_body.__contains__("college") or comment_body.__contains__("student") \
                or comment_body.__contains__("teacher") or comment_body.__contains__("professor"):
            new_comment = f"{comment.split('$$,$$')[0]}$$,$${comment.split('$$,$$')[2]}$$,$${comment.split('$$,$$')[4]}"
        else:
            new_comment = ""
        return str(new_comment)


