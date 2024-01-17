package models

type Manga struct {
	UserID uint   `gorm:"primaryKey;autoIncrement:false" json:"-"`
	ID     string `gorm:"primaryKey;autoIncrement:false" json:"id"`
	Driver string `gorm:"primaryKey;autoIncrement:false" json:"driver"`
}
