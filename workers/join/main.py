#!/usr/bin/env python3
import logging
import os
from join import Join

def initialize_config():
    config_params = {}
    try:
        config_params["queue_to_read_2"] = os.environ["QUEUE_TO_READ_2"]
        config_params["queue_to_read_3"] = os.environ["QUEUE_TO_READ_3"]
        config_params["queues_to_write"] = os.environ["QUEUES_TO_WRITE"].split("|")
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting".format(e))

    return config_params

def main():
    initialize_log()
    config_params = initialize_config()
    join = Join(config_params["queue_to_read_2"], config_params["queue_to_read_3"], config_params["queues_to_write"])
    join.start()

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