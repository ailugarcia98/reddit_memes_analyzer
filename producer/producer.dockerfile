FROM ubuntu:20.04

RUN apt update && apt install python3 python3-pip -y
RUN pip3 install pika

COPY producer.py /
COPY main.py /
COPY config.ini /
COPY middleware middleware/
CMD ["python3", "./main.py"]