#!/bin/bash

set -e  # Exit on any error

# Constants
RABBITMQ_CONTAINER_NAME="rabbitmq-server"
RABBITMQ_IMAGE="rabbitmq:3-management"

echo "Building Container..."
docker build -t rabbitmq_analysis .

echo "Setting up RabbitMQ..."

# Check if a container with the RabbitMQ name exists
if docker ps -a --format '{{.Names}}' | grep -q "^${RABBITMQ_CONTAINER_NAME}$"; then
    echo "A container named '${RABBITMQ_CONTAINER_NAME}' already exists."
    read -p "Do you want to remove it and recreate? [y/N]: " choice
    case "$choice" in
        y|Y )
            echo "Removing existing container..."
            docker rm -f "${RABBITMQ_CONTAINER_NAME}"
            ;;
        * )
            echo "Exiting setup. Use the existing container or remove it manually."
            exit 1
            ;;
    esac
fi

# Pull the latest RabbitMQ image
echo "Pulling the RabbitMQ image..."
docker pull "${RABBITMQ_IMAGE}"

# Run RabbitMQ container
echo "Starting RabbitMQ container..."
docker run -d --name "${RABBITMQ_CONTAINER_NAME}" --hostname "${RABBITMQ_CONTAINER_NAME}" \
    -p 5672:5672 -p 15672:15672 "${RABBITMQ_IMAGE}"

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ to initialize..."
while ! curl -s http://localhost:15672 > /dev/null; do
    sleep 2
done

echo "RabbitMQ is up and running!"
echo "Access the RabbitMQ management interface at http://localhost:15672"
echo "Default credentials: Username = guest, Password = guest"




# Start the Producer
echo "Running Producer..."
docker run --rm --name producer --network="host" rabbitmq_analysis python producer.py
echo "Success!"

# Start Workers
echo "Running Workers..."
docker run --rm --name worker1 --network="host" rabbitmq_analysis python worker.py 
wait
echo "Success!"

# Combine Results
echo "Combining Data..."
docker run --rm --name aggregator --network="host" rabbitmq_analysis python aggregator.py

# Generate Graph
echo "Plotting..."
docker run --rm --name plotter --network="host" rabbitmq_analysis python plot_results.py
