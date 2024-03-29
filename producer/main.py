#!/usr/bin/env python3
import logging
import os
from configparser import ConfigParser
from producer import Producer
from middleware.middleware import Middleware

def initialize_config():
    """ Parse env variables or config file to find program config params
    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file.
    If at least one of the config parameters is not found a KeyError exception
    is thrown. If a parameter could not be parsed, a ValueError is thrown.
    If parsing succeeded, the function returns a ConfigParser object
    with config parameters
    """
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["post_queue_name"] = config["DEFAULT"]["post_queue_name"]
        config_params["post_file"] = config["DEFAULT"]["post_file"]
        config_params["comments_queue_name"] = config["DEFAULT"]["comments_queue_name"]
        config_params["comments_file"] = config["DEFAULT"]["comments_file"]
        config_params["size_send"] = int(config["DEFAULT"]["size_send"])
        config_params["queue_response_avg"] = config["DEFAULT"]["queue_response"].split('|')[0]
        config_params["queue_response_url"] = config["DEFAULT"]["queue_response"].split('|')[1]
        config_params["queue_response_meme"] = config["DEFAULT"]["queue_response"].split('|')[2]
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting".format(e))

    return config_params

def main():
    initialize_log()

    config_params = initialize_config()

    middleware = Middleware('rabbitmq')

    producer = Producer(config_params["post_queue_name"], config_params["post_file"], \
                        config_params["comments_queue_name"], config_params["comments_file"], \
                        config_params["size_send"], config_params["queue_response_avg"], \
                        config_params["queue_response_url"], config_params["queue_response_meme"], \
                        middleware)
    producer.start()
    middleware.close()

def initialize_log():
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__== "__main__":
    main()