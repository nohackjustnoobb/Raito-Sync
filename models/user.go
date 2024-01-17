package models

type User struct {
	ID          uint     `gorm:"primarykey" json:"id"`
	CreatedAt   uint     `gorm:"autoCreateTime:milli" json:"createdAt"`
	UpdatedAt   uint     `gorm:"autoUpdateTime:milli" json:"updatedAt"`
	Email       string   `gorm:"unique" json:"email"`
	Password    string   `json:"-"`
	Settings    *string  `json:"-"`
	Collections []Manga  `gorm:"foreignKey:UserID;constraint:OnDelete:CASCADE" json:"-"`
	Histories   []Record `gorm:"foreignKey:UserID;constraint:OnDelete:CASCADE" json:"-"`
}
