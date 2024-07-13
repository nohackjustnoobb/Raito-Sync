package models

type Record struct {
	UserID uint   `gorm:"primaryKey;autoIncrement:false" json:"-"`
	ID     string `gorm:"primaryKey;autoIncrement:false" json:"id"`
	Driver string `gorm:"primaryKey;autoIncrement:false" json:"driver"`

	Title          string `json:"title"`
	Thumbnail      string `json:"thumbnail"`
	Latest         string `json:"latest"`
	IsUpdated      bool   `json:"isUpdated"`
	Datetime       uint   `json:"datetime"`
	UpdateDatetime *uint  `json:"updateDatetime"`

	ChapterID    *string `json:"chapterId"`
	ChapterTitle *string `json:"chapterTitle"`
	Page         *uint   `json:"page"`

	UpdatedAt uint `gorm:"autoUpdateTime:milli" json:"-"`
}
