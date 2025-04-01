import pika
import time

# การเชื่อมต่อ RabbitMQ
def connect_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            print("✅ Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("⏳ Waiting for RabbitMQ...")
            time.sleep(5)

# ใช้ฟังก์ชันเชื่อมต่อ RabbitMQ
connection = connect_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

# ส่ง task 100,000 ตัวใน batch ของ 1000
num_tasks = 100000
batch_size = 1000

for i in range(0, num_tasks, batch_size):
    for task_id in range(i, i + batch_size):
        task = f"Task {task_id + 1}"
        channel.basic_publish(exchange='', routing_key='task_queue', body=task)
        print(f"Sent: {task}")
    print(f"Sent batch {i // batch_size + 1} of {num_tasks // batch_size}")
    
connection.close()
