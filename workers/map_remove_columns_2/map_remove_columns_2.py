#!/usr/bin/env python3
import json


class MapRemoveColumns2:
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
        comments = [json.loads(body)]
        if comments == [{}]:
            new_body = json.dumps({})
            for queue in self.queues_to_write:
                self.middleware.publish(queue, new_body)
        else:
            for comment in comments:
                new_body = self.new_body(comment)
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, new_body)

    def new_body(self, body):
        post_id = body["permalink"].split('/')[6]
        body["post_id"] = post_id
        return f'{body["post_id"]},{body["body"]},{body["score"]},{body["sentiment"]}'


