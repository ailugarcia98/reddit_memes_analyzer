import pika
import sys


class Middleware:
    def __init__(self, mom_host):
        # Create RabbitMQ communication channel
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=mom_host, heartbeat=3600))
        self.channel = self.connection.channel()

    def declare(self, queue):
        self.channel.queue_declare(queue=queue, durable=True)

    def publish(self, queue, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def subscribe(self, queue, callback_function):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue, on_message_callback=callback_function)

    def ack(self, method):
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def wait_for_messages(self):
        self.channel.start_consuming()

    def shutdown(self):
        self.channel.stop_consuming()

    def close(self):
        self.connection.close()
