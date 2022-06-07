#!/usr/bin/env python3


class MapRemoveColumns5:
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
        body_recv = eval(body.decode('utf-8'))
        url = self.new_body(body_recv).encode('utf-8')
        for queue in self.queues_to_write:
            self.middleware.publish(queue, url)

    def new_body(self, body):
        url = body[0]
        return f"{url}"


