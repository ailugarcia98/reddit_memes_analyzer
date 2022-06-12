#!/usr/bin/env python3
import json
import logging
import signal
import sys


class FilterDeletedRemoved:
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
        comments = json.loads(body)
        if comments == {}:
            new_body = json.dumps({})
            for queue in self.queues_to_write:
                self.middleware.publish(queue, new_body)
            logging.info(f"[FILTER DELETED REMOVED] END")
            self.middleware.ack(method)
            self.middleware.shutdown()
        else:
            send_array = []
            for comment in comments:
                comments_not_deleted_removed = self.new_body(comment)
                if comments_not_deleted_removed != json.dumps("removed/deleted"):
                    send_array.append(comments_not_deleted_removed)
            if len(send_array) > 0:
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, json.dumps(send_array))
            self.middleware.ack(method)

    def new_body(self, comment):
        if comment["body"] == "[removed]" or comment["body"] == "[deleted]":
            new_comment = "removed/deleted"
        else:
            new_comment = comment
        return json.dumps(new_comment)


