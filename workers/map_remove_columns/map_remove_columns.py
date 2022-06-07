#!/usr/bin/env python3
import json


class MapRemoveColumns:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.middleware = middleware

    def start(self):

        self.middleware.declare(self.queue_to_read)
        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.subscribe(self.queue_to_read, self.callback)
        self.middleware.wait_for_messages()

    def callback(self, ch, method, properties, body):
        posts = json.loads(body)
        if posts == {}:
            new_body = json.dumps({})
            for queue in self.queues_to_write:
                self.middleware.publish(queue, new_body)
        else:
            for post in posts:
                new_body = self.new_body(post).encode('utf-8')
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, new_body)

    def new_body(self, body):
        return f'{body["id"]}, {body["score"]}'


