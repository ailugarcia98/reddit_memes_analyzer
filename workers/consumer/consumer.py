#!/usr/bin/env python3
import json


class Consumer:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.middleware = middleware

    def start(self):

        self.middleware.declare(self.queue_to_read)

        for queue in self.queues_to_write:
            # channel.queue_declare(queue=queue, durable=True)
            self.middleware.declare(queue)

        self.middleware.subscribe(self.queue_to_read, self.callback)

        self.middleware.wait_for_messages()

        self.middleware.close()

    def callback(self, ch, method, properties, body):
        for queue in self.queues_to_write:
            if json.loads(body) == json.dumps({}):
                body = json.dumps({})
            self.middleware.publish(queue, body)
