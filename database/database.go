package database

import (
	"Raito-Sync/models"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var (
	Conn *gorm.DB
)

func Setup() {
	var err error
	Conn, err = gorm.Open(sqlite.Open("db.sqlite3"))
	if err != nil {
		panic("failed to connect database")
	}

	Conn.AutoMigrate(&models.User{})
	Conn.AutoMigrate(&models.Manga{})
	Conn.AutoMigrate(&models.Record{})
}
