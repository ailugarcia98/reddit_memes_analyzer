#!/usr/bin/env python3

class FilterScoreMayorAvg:
    def __init__(self, queue_to_read_avg, queue_to_read_filter, queues_to_write, middleware):
        self.queue_to_read_avg = queue_to_read_avg
        self.queue_to_read_filter = queue_to_read_filter
        self.queues_to_write = queues_to_write
        self.avg = 0.0
        self.middleware = middleware

    def start(self):

        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.declare(self.queue_to_read_avg)
        self.middleware.subscribe(self.queue_to_read_avg, self.callback_avg)

        self.middleware.declare(self.queue_to_read_filter)
        self.middleware.subscribe(self.queue_to_read_filter, self.callback_filter)

        self.middleware.wait_for_messages()

        self.middleware.close()

    def callback_filter(self, ch, method, properties, body):
        score_body = float(body.decode('utf-8').split(',')[1])
        if score_body > self.avg:
            url = str(body.decode('utf-8').split(',')[2])
            for queue in self.queues_to_write:
                self.middleware.publish(queue, url.encode('utf-8'))

    def callback_avg(self, ch, method, properties, body):
        self.avg = float(eval(body.decode('utf-8')))




