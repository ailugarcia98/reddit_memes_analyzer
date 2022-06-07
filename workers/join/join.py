#!/usr/bin/env python3


class Join:
    def __init__(self, queue_to_read_2, queue_to_read_3, queues_to_write, middleware):
        self.queue_to_read_comments = queue_to_read_2
        self.queue_to_read_posts = queue_to_read_3
        self.queues_to_write = queues_to_write
        self.posts = []
        self.comments = []
        self.new_body = []
        self.end = False
        self.stop_append_post = False
        self.stop_append_comments = False
        self.middleware = middleware

    def start(self):

        for queue in self.queues_to_write:
            self.middleware.declare(queue)

        self.middleware.declare(self.queue_to_read_posts)
        self.middleware.subscribe(self.queue_to_read_posts, self.callback_post)

        self.middleware.declare(self.queue_to_read_comments)
        self.middleware.subscribe(self.queue_to_read_comments, self.callback_comments)

        self.middleware.wait_for_messages()
        self.middleware.close()

    def contains_end(self, array):
        contains = False
        for i in array:
            if array[i] == str({}):
                contains = True
        return contains

    def callback_post(self, ch, method, properties, body):
        real_body = body.decode('utf-8')
        if not self.stop_append_post:
            if real_body == str({}):
                self.stop_append_post = True
            self.posts.append(real_body)

    def callback_comments(self, ch, method, properties, body):
        real_body = body.decode('utf-8')
        if not self.stop_append_comments:
            if real_body == str({}):
                self.stop_append_comments = True
            self.comments.append(real_body)

        for post in self.posts:
            post_id = post.split(',')[0]
            for comment in self.comments:
                if post == str({}) and comment == str({}):
                    self.end = True
                    self.new_body.append(str({}))
                    for queue in self.queues_to_write:
                        self.middleware.publish(queue, str(self.new_body).encode('utf-8'))
                    return 0
                else:
                    comment_post_id = comment.split(',')[0]
                    if post_id == comment_post_id:
                        post_url = post.split(',')[1]
                        if f'{comment},{post_url}' not in self.new_body:   # drop duplicates
                            self.new_body.append(f'{comment},{post_url}')
