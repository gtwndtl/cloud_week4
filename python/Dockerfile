# ใช้ Python 3.9 เป็น base image
FROM python:3.9-slim

# ติดตั้ง libpq-dev เพื่อให้สามารถคอมไพล์ psycopg2 ได้
RUN apt-get update && apt-get install -y libpq-dev

# ตั้ง working directory ใน container
WORKDIR /app

# คัดลอกไฟล์ทั้งหมดจากโฟลเดอร์โปรเจกต์ไปยัง container
COPY . /app

# ติดตั้ง dependencies ที่จำเป็นจาก requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ติดตั้ง Prometheus client สำหรับการเก็บข้อมูล metric
RUN pip install prometheus_client

# ติดตั้ง libpq-dev หากใช้ psycopg2 สำหรับการเชื่อมต่อ PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev

# ตั้งค่า environment variables (สามารถใช้ .env เพื่อเก็บข้อมูลสำคัญ)
ENV RABBITMQ_HOST=rabbitmq
ENV DB_NAME=mydatabase
ENV DB_USER=postgres
ENV DB_PASSWORD=admin
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV QUEUE_NAME=result_queue
ENV PUSHGATEWAY_URL=http://localhost:9091

# รันสคริปต์ทั้งหมดตามลำดับ (send_task.py -> collector.py -> worker.py)
CMD python send_task.py && python collector.py && python worker.py
