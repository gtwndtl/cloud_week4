import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

# Sending 100,000 tasks in batches of 1000
num_tasks = 100000
batch_size = 1000

for i in range(0, num_tasks, batch_size):
    for task_id in range(i, i + batch_size):
        task = f"Task {task_id + 1}"
        channel.basic_publish(exchange='', routing_key='task_queue', body=task)
        print(f"Sent: {task}")
    print(f"Sent batch {i // batch_size + 1} of {num_tasks // batch_size}")
    
connection.close()
