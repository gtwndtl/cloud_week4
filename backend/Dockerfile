# ใช้ base image ของ Go
FROM golang:1.23.3

# ตั้งค่า working directory
WORKDIR /app

# คัดลอกไฟล์ทั้งหมดเข้า container
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# ติดตั้งไลบรารี .env
RUN go get github.com/joho/godotenv

# คอมไพล์โปรแกรม
RUN go build -o main .

# รัน backend
CMD ["./main"]
