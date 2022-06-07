#!/usr/bin/env python3
import logging
import os
from map_remove_columns_2 import MapRemoveColumns2
from middleware.middleware import Middleware

def initialize_config():
    config_params = {}
    try:
        config_params["queue_to_read"] = os.environ["QUEUE_TO_READ"]
        config_params["queues_to_write"] = [os.environ["QUEUES_TO_WRITE"]] #add split
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting".format(e))

    return config_params

def main():
    initialize_log()
    config_params = initialize_config()
    middleware = Middleware('rabbitmq')
    mrcolumns2 = MapRemoveColumns2(config_params["queue_to_read"], config_params["queues_to_write"], middleware)
    mrcolumns2.start()

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