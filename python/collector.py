import psycopg2
import pika
import os
import time
from dotenv import load_dotenv

# 🔹 โหลด Environment Variables จาก .env
load_dotenv()

# ค่าต่าง ๆ สำหรับเชื่อมต่อกับ DB และ RabbitMQ
DB_NAME = os.getenv("DB_NAME", "mydatabase")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_HOST = os.getenv("DB_HOST", "postgres")  # Docker ใช้ 'postgres' เป็น hostname
DB_PORT = os.getenv("DB_PORT", "5432")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")  # Docker ใช้ 'rabbitmq' เป็น hostname
QUEUE_NAME = "result_queue"

# 🔹 ฟังก์ชันเชื่อมต่อฐานข้อมูล
def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            print(f"✅ Connected to PostgreSQL: {DB_NAME}")
            return conn
        except Exception as e:
            print("⏳ Waiting for PostgreSQL...")
            time.sleep(5)

# 🔹 สร้างฐานข้อมูลถ้ายังไม่มี
def setup_database():
    conn = connect_db()
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"✅ Created database: {DB_NAME}")
    
    cursor.close()
    conn.close()

# 🔹 สร้างตาราง
def setup_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            data TEXT NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table 'results' is ready")

# 🔹 ฟังก์ชันบันทึกข้อมูลลงฐานข้อมูล
def save_to_db(data):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO results (data) VALUES (%s)", (data,))
        conn.commit()
        print("💾 Data saved to PostgreSQL:", data)
    except Exception as e:
        print("❌ Database error:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# 🔹 ฟังก์ชันเชื่อมต่อ RabbitMQ
def connect_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST, heartbeat=600, blocked_connection_timeout=300
                )
            )
            return connection
        except Exception as e:
            print("⏳ Waiting for RabbitMQ...")
            time.sleep(5)

# 🔹 ฟังก์ชันรับข้อความจากคิว
def callback(ch, method, properties, body):
    message = body.decode()
    print(f"📥 Received: {message}")
    save_to_db(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    setup_database()
    setup_table()

    # เชื่อมต่อ RabbitMQ
    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("🚀 Waiting for results...")
    channel.start_consuming()