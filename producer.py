import pika
import json

# RabbitMQ Connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='task_queue', durable=True)

# Publish tasks
files = ['data_A', 'data_B', 'data_C', 'data_D']
for file in files:
    task = json.dumps({"file": file})
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=task,
        properties=pika.BasicProperties(delivery_mode=2)  # Make messages persistent
    )
    print(f"Task queued for {file}")

connection.close()
