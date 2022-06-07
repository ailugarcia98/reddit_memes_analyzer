#!/usr/bin/env python3
import logging
import os
from filter_score_mayor_avg import FilterScoreMayorAvg
from middleware.middleware import Middleware

def initialize_config():
    config_params = {}
    try:
        config_params["queue_to_read_avg"] = os.environ["QUEUE_TO_READ_AVG"]
        config_params["queue_to_read_filter"] = os.environ["QUEUE_TO_READ_FILTER"]
        config_params["queues_to_write"] = [os.environ["QUEUES_TO_WRITE"]]
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting".format(e))

    return config_params

def main():
    initialize_log()
    config_params = initialize_config()
    middleware = Middleware('rabbitmq')
    filter = FilterScoreMayorAvg(config_params["queue_to_read_avg"], config_params["queue_to_read_filter"], \
                                 config_params["queues_to_write"], middleware)
    filter.start()

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