#!/usr/bin/env python3
import json
import logging
import signal
import sys


class Join:
    def __init__(self, queue_to_read_2, queue_to_read_3, queues_to_write, middleware):
        self.queue_to_read_comments = queue_to_read_2
        self.queue_to_read_posts = queue_to_read_3
        self.queues_to_write = queues_to_write
        self.new_body = {}
        self.end = False
        self.stop_append_post = False
        self.stop_append_comments = False
        self.middleware = middleware
        # graceful quit
        # Define how to do when it will receive SIGTERM
        signal.signal(signal.SIGTERM, self.__need_to_stop)
        signal.signal(signal.SIGINT, self.__need_to_stop)

    def __need_to_stop(self, *args):
        self.middleware.shutdown()
        sys.exit(0)

    def start(self):

        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.declare(self.queue_to_read_posts)
        self.middleware.subscribe(self.queue_to_read_posts, self.callback_post)

        self.middleware.declare(self.queue_to_read_comments)
        self.middleware.subscribe(self.queue_to_read_comments, self.callback_comments)

        self.middleware.wait_for_messages()

    def contains_end(self, array):
        contains = False
        for i in array:
            if array[i] == str({}):
                contains = True
        return contains

    def callback_post(self, ch, method, properties, body):
        real_body = json.loads(body)
        if not self.stop_append_post:
            if real_body == json.loads('{}'):
                logging.info(f"[JOIN] STOP APPEND POSTS")
                self.stop_append_post = True
                self.middleware.ack(method)
                if self.stop_append_comments:
                    self.do_join()
            else:
                for post in real_body:
                    post_id = str(post.split(',')[0])
                    if post_id not in self.new_body and str(post.split(',')[1]) != '':
                        self.new_body.update({post_id: {"url": str(post.split(',')[1]), "comments": []}})
                    else:
                        if post_id in self.new_body:
                            if self.new_body[post_id]["url"] == '' and str(post.split(',')[1]) != '':
                                self.new_body[post_id]["url"] = str(post.split(',')[1])
                self.middleware.ack(method)
        else:
            self.middleware.ack(method)

    def callback_comments(self, ch, method, properties, body):
        real_body = json.loads(body)
        if not self.stop_append_comments:
            if real_body == json.loads('{}'):
                logging.info(f"[JOIN] STOP APPEND COMMENTS")
                self.stop_append_comments = True
                self.middleware.ack(method)
                if self.stop_append_post:
                    self.do_join()
            else:
                for comment in real_body:
                    post_id = str(comment.split('$$,$$')[0])
                    if post_id in self.new_body:
                        comment_split = comment.split('$$,$$')
                        body_score_sentiment = f"{comment_split[1]}$$,$${comment_split[2]}$$,$${comment_split[3]}"
                        self.new_body[post_id]["comments"].append(body_score_sentiment)
                    else:
                        if not self.stop_append_post:
                            comment_split = comment.split('$$,$$')
                            self.new_body.update({post_id: {"url": '', "comments": \
                                [f"{comment_split[1]}$$,$${comment_split[2]}$$,$${comment_split[3]}"]}})
                self.middleware.ack(method)
        else:
            self.middleware.ack(method)

    def do_join(self):
        body_to_send = []
        for post_id in self.new_body:
            url = self.new_body[post_id]["url"]
            if url != '':
                for comment in self.new_body[post_id]["comments"]:
                    post_url = url
                    body_to_send.append(f'{post_id}$$,$${comment}$$,$${post_url}')
        body_to_send.append(str({}))
        for queue in self.queues_to_write:
            self.middleware.publish(queue, json.dumps(body_to_send))
