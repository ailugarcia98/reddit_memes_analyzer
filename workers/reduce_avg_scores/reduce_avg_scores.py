#!/usr/bin/env python3
import logging


class ReduceAvgScores:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.avg_score = 0
        self.middleware = middleware

    def start(self):

        self.middleware.declare(self.queue_to_read)
        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.subscribe(self.queue_to_read, self.callback)
        self.middleware.wait_for_messages()

    def callback(self, ch, method, properties, body):
        post = body.decode('utf-8')
        new_body = post.split(',')
        if int(new_body[1]) != 0:
            avg = int(new_body[0])/int(new_body[1])
            avg_encode = str(avg).encode('utf-8')
            for queue in self.queues_to_write:
                self.middleware.publish(queue, avg_encode)
        else:
            logging.error("Div 0 error")




