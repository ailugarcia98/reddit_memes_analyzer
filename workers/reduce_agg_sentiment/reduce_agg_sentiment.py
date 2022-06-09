#!/usr/bin/env python3
import signal
import sys


class ReduceAggSentiment:
    def __init__(self, queue_to_read, queues_to_write, middleware):
        self.queue_to_read = queue_to_read
        self.queues_to_write = queues_to_write
        self.dict_sentiment = []
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
        comment = body.decode('utf-8')
        if comment == str({}):
            new_body = str(self.agg()).encode('utf-8')
            for queue in self.queues_to_write:
                self.middleware.publish(queue, new_body)
            self.middleware.shutdown()
        else:
            self.new_body(comment)

    def new_body(self, comment):
        maybe_sentiment = comment.split('$$,$$')[1]
        if maybe_sentiment != str(''):
            sentiment = float(comment.split('$$,$$')[1])
            post_id = comment.split('$$,$$')[0]
            url = comment.split('$$,$$')[2]
            self.dict_sentiment.append((post_id,  url, sentiment, int(1)))

    def agg(self):
        old_body = {}
        new_body = []
        urls = []
        for post_id, url, sentiment, count in self.dict_sentiment:
            if url not in urls:
                urls.append(url)
            try:
                prev_sentiment, prev_count = old_body[url]
            except KeyError:
                old_body[url] = float(sentiment), int(count)
            else:
                new_sentiment = float(sentiment) + float(prev_sentiment)
                new_count = int(prev_count) + int(count)
                old_body[url] = new_sentiment, new_count

        for url in urls:
            new_body.append([url, old_body[url][0], old_body[url][1]])

        return new_body


