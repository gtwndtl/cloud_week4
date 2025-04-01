# ใช้ Node.js image เป็น base
FROM node:18-alpine

# กำหนด working directory
WORKDIR /frontend

# คัดลอกไฟล์ package.json และติดตั้ง dependencies
COPY package*.json ./
RUN npm install

# คัดลอกไฟล์ทั้งหมดจาก project directory ไปยัง container
COPY . .

# เปิดพอร์ตที่ Vite ใช้
EXPOSE 5173

# Start Vite
CMD ["npm", "run", "dev"]