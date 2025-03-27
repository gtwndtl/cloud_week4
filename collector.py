import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='result_queue', durable=True)

def callback(ch, method, properties, body):
    print(f"Collector received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='result_queue', on_message_callback=callback)

print("Waiting for results...")
channel.start_consuming()
