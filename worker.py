import pika
import time
import random
import socket
from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway

# Configurations
RABBITMQ_HOST = "localhost"
PUSHGATEWAY_URL = "http://localhost:9091"
WORKER_ID = f"Worker-{random.randint(1, 100)}"
HOSTNAME = socket.gethostname()

# Create Prometheus Registry
registry = CollectorRegistry()
TASKS_COMPLETED = Counter('worker_tasks_completed', 'Total tasks completed', registry=registry)
TASK_DURATION = Gauge('worker_task_duration_seconds', 'Duration of last task in seconds', registry=registry)
WORKER_UP = Gauge('worker_up', 'Worker status (1=up, 0=down)', ['hostname'], registry=registry)

def push_metrics():
    push_to_gateway(PUSHGATEWAY_URL, job=WORKER_ID, registry=registry)

def process_task():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)

    print(f"{WORKER_ID} waiting for tasks...")

    def callback(ch, method, properties, body):
        task = body.decode()
        print(f"{WORKER_ID} received: {task}")

        # Simulate task processing
        start_time = time.time()
        time_to_sleep = random.randint(1, 3)
        time.sleep(time_to_sleep)
        end_time = time.time()

        # Update and push metrics
        TASKS_COMPLETED.inc()
        TASK_DURATION.set(end_time - start_time)
        WORKER_UP.labels(hostname=HOSTNAME).set(1)  # Mark worker as up
        push_metrics()

        # Send result back
        result = f"Result from {WORKER_ID}: {task} processed in {time_to_sleep}s"
        channel.basic_publish(exchange='', routing_key='result_queue', body=result)
        print(f"{WORKER_ID} sent result")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"{WORKER_ID} shutting down...")
        WORKER_UP.labels(hostname=HOSTNAME).set(0)  # Mark worker as down
        push_metrics()

process_task()
