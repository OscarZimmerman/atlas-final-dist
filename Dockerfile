# Base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy application files to the container
COPY requirements.txt /app/
COPY process.py /app/
COPY producer.py /app/
COPY worker.py /app/
COPY aggregator.py /app/
COPY plot_results.py /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install RabbitMQ client library pika
RUN pip install --no-cache-dir pika==1.3.1

# Expose RabbitMQ default port (if RabbitMQ is running inside this container)
EXPOSE 5672

# Command to run when the container starts
CMD ["bash"]
