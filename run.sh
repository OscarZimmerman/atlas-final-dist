#!/bin/bash
set -e

echo "Starting RabbitMQ server..."
rabbitmq-server -detached

echo "Queuing tasks..."
python producer.py

echo "Starting workers..."
docker-compose up --scale worker=4  # Adjust the number of workers

echo "Combining results..."
python aggregator.py

echo "Plotting results..."
python plot_results.py  # Use your existing plotting code
