#!/usr/bin/env python3
import logging

import requests
import signal
import sys


class DownloadMeme:
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
        meme_to_download = body.decode('utf-8')
        if meme_to_download != '':
            meme_downloaded = self.download_meme(meme_to_download)
            if meme_downloaded is not None:
                for queue in self.queues_to_write:
                    self.middleware.publish(queue, meme_downloaded)
        logging.info(f"[DOWNLOAD MEME] END")
        self.middleware.ack(method)

    def download_meme(self, url):
        if url.__contains__(".jpg") or url.__contains__(".png") or url.__contains__(".gif"):
            logging.info(f"[DOWNLOADER] Downloading meme {url}")
            response = requests.get(url)
            if response.status_code == 200:
                meme = response.content
            else:
                meme = None
            return meme
        else:
            logging.info("[DOWNLOADER] This meme isn't an image/gif")
            return None
