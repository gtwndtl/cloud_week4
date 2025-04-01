package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv" // ใช้สำหรับโหลด .env
	"github.com/rs/cors"
	_ "github.com/lib/pq"
)

// Struct สำหรับข้อมูลที่ได้จาก DB
type Result struct {
	ID         int    `json:"id"`
	Data       string `json:"data"`
	ReceivedAt string `json:"received_at"`
}

// ตัวแปรเชื่อมต่อ DB (ใช้ connection pool)
var db *sql.DB

// ฟังก์ชันเชื่อมต่อกับฐานข้อมูล
func initDB() {
	var err error

	// โหลด Environment Variables จาก .env
	err = godotenv.Load()
	if err != nil {
		log.Println("⚠️ ไม่พบไฟล์ .env, ใช้ค่าจากระบบแทน")
	}

	// อ่านค่าจาก Environment Variables
	DB_HOST := os.Getenv("DB_HOST")
	DB_PORT := os.Getenv("DB_PORT")
	DB_USER := os.Getenv("DB_USER")
	DB_PASSWORD := os.Getenv("DB_PASSWORD")
	DB_NAME := os.Getenv("DB_NAME")

	// Connection string
	psqlInfo := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
	)

	// สร้าง Connection
	db, err = sql.Open("postgres", psqlInfo)
	if err != nil {
		log.Fatal("🚨 เชื่อมต่อ Database ไม่ได้: ", err)
	}

	// ตรวจสอบการเชื่อมต่อ
	err = db.Ping()
	if err != nil {
		log.Fatal("🚨 ไม่สามารถ Ping Database ได้: ", err)
	}

	log.Println("✅ เชื่อมต่อ PostgreSQL สำเร็จ!")
}

// ฟังก์ชันดึงข้อมูลจากฐานข้อมูล
func getResults(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, data, received_at FROM results")
	if err != nil {
		http.Error(w, "Error fetching data from database", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var results []Result
	for rows.Next() {
		var result Result
		err := rows.Scan(&result.ID, &result.Data, &result.ReceivedAt)
		if err != nil {
			http.Error(w, "Error scanning data", http.StatusInternalServerError)
			return
		}
		results = append(results, result)
	}

	// ส่งข้อมูลเป็น JSON
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(results)
}

func getApi(w http.ResponseWriter, r *http.Request) {
	// สร้างข้อมูล JSON
	response := map[string]string{
		"message": "Hello World",
	}
	// ส่งข้อมูลเป็น JSON
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// ฟังก์ชันหลัก
func main() {
	// เชื่อมต่อ DB
	initDB()
	defer db.Close()

	// สร้าง Router
	router := mux.NewRouter()

	// กำหนด API Endpoint
	router.HandleFunc("/api/results", getResults).Methods("GET")
	router.HandleFunc("/api", getApi).Methods("GET")

	// ตั้งค่า CORS
	corsHandler := cors.New(cors.Options{
		AllowedOrigins:   []string{"http://localhost:5173", "http://localhost:3000"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE"},
		AllowedHeaders:   []string{"Content-Type"},
		AllowCredentials: true,
	})

	// รันเซิร์ฟเวอร์
	PORT := os.Getenv("PORT")
	if PORT == "" {
		PORT = "8000"
	}

	handler := corsHandler.Handler(router)
	log.Println("🚀 Server running at http://localhost:" + PORT)
	log.Fatal(http.ListenAndServe(":"+PORT, handler))
}
