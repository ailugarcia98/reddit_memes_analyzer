#!/usr/bin/env python3
import pika
import sys
import random
import time
import csv
import json

# Wait for rabbitmq to come up
print("Sleep")
time.sleep(20)
print("Wake up")

# Create RabbitMQ communication channel
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()


channel.queue_declare(queue='task_queue', durable=True)

try:
    with open('/csvs/posts.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print("Fila de csv %r" % row)
            message = json.dumps(row)
            channel.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=message,
                properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
            print(" [x] Sent %r" % message)
            time.sleep(1)
except Exception as e:
    print(e)

connection.close()