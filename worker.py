import pika
import json
import pandas as pd
from process import read_file

# Establish RabbitMQ connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', heartbeat=600)
)

channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
channel.basic_qos(prefetch_count=1)  # Ensure one message is processed at a time

def callback(ch, method, properties, body):
    """
    Callback to process messages and acknowledge them.
    """
    task = json.loads(body)
    file = task.get('file')
    print(f"Received message for file: {file} with delivery_tag: {method.delivery_tag}")

    try:
        # Simulate file processing
        data = read_file(
            f"https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/GamGam/Data/{file}.GamGam.root",
            file
        )
        data.to_csv(f"output_{file}.csv")
        print(f"Finished processing file: {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")
    finally:
        try:
            print(f"Acknowledging delivery_tag: {method.delivery_tag}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ack_error:
            print(f"Error during acknowledgment for delivery_tag {method.delivery_tag}: {ack_error}")

channel.basic_consume(queue='task_queue', on_message_callback=callback)
print("Waiting for messages...")
channel.start_consuming()
