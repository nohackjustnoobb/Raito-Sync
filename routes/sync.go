package routes

import (
	"Raito-Sync/database"
	"Raito-Sync/models"
	"crypto/md5"
	"encoding/hex"
	"sort"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
)

func SetupSyncRoutes(app *fiber.App) {
	app.Get("/settings", getSettings)
	app.Post("/settings", setSettings)

	app.Get("/collections", getCollections)
	app.Post("/collections", addCollections)
	app.Delete("/collections", removeCollections)

	app.Get("/history", getRecords)
	app.Post("/history", updateRecords)
	app.Delete("/history", resetRecords)

	app.Get("/sync", getSync)
}

type SettingsInfo struct {
	Settings *string `json:"settings"`
}

func getSync(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	user := new(models.User)
	database.Conn.Model(&models.User{}).Preload("Collections").First(user, claims["uid"].(float64))

	// hash the collections
	mangaSlice := []string{}
	for _, manga := range user.Collections {
		mangaSlice = append(mangaSlice, manga.Driver+manga.ID)
	}
	sort.Strings(mangaSlice)

	mangaString := ""
	for _, manga := range mangaSlice {
		mangaString += manga
	}
	collectionsHash := md5.Sum([]byte(mangaString))

	// hash only the latest record
	record := new(models.Record)
	result := database.Conn.Where("user_id = ? ", user.ID).Order("-datetime").Limit(1).Find(record)
	recordString := ""
	if result.RowsAffected == 1 {
		recordString += record.Driver
		recordString += record.ID
		recordString += strconv.FormatUint(uint64(record.Datetime), 10)
	}
	recordHash := md5.Sum([]byte(recordString))

	// hash settings
	settings := ""
	if user.Settings != nil {
		settings = *user.Settings
	}
	settingsHash := md5.Sum([]byte(settings))

	return c.JSON(fiber.Map{
		"settings":    hex.EncodeToString(settingsHash[:]),
		"history":     hex.EncodeToString(recordHash[:]),
		"collections": hex.EncodeToString(collectionsHash[:]),
	})
}

func getSettings(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	user := new(models.User)
	database.Conn.First(user, claims["uid"].(float64))

	return c.JSON(fiber.Map{"settings": user.Settings})
}

func setSettings(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	user := new(models.User)
	database.Conn.First(user, claims["uid"].(float64))

	info := new(SettingsInfo)
	if err := c.BodyParser(info); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	user.Settings = info.Settings
	database.Conn.Save(user)

	c.Status(fiber.StatusAccepted)
	return c.JSON(fiber.Map{"settings": user.Settings})
}

func getCollections(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	collections := []models.Manga{}
	database.Conn.Where("user_id = ?", claims["uid"]).Find(&collections)

	return c.JSON(collections)
}

func addCollections(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	uid := uint(claims["uid"].(float64))
	collections := []models.Manga{}
	database.Conn.Where("user_id = ?", uid).Find(&collections)

	// get the mangas
	mangas := []models.Manga{}
	if err := c.BodyParser(&mangas); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	// check if duplicated
	filtered := []models.Manga{}
	for _, manga := range mangas {
		isDuplicated := false
		for _, collection := range collections {
			if collection.ID == manga.ID && collection.Driver == manga.Driver {
				isDuplicated = true
				break
			}
		}
		if !isDuplicated {
			manga.UserID = uid
			filtered = append(filtered, manga)
		}
	}

	// save the collections
	if len(filtered) > 0 {
		database.Conn.Save(&filtered)
		database.Conn.Where("user_id = ?", uid).Find(&collections)
	}

	c.Status(fiber.StatusAccepted)
	return c.JSON(collections)
}

func removeCollections(c *fiber.Ctx) error {
	// get info
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	driver := c.Query("driver")
	id := c.Query("id")

	if driver == "" || id == "" {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": `\"driver\" or \"id\" are missing.`})
	}

	manga := models.Manga{
		UserID: uint(claims["uid"].(float64)),
		Driver: driver,
		ID:     id,
	}
	database.Conn.Delete(&manga)

	c.Status(fiber.StatusNoContent)
	return nil
}

func getRecords(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	records := []models.Record{}

	var err error

	rawPage := c.Query("page")
	page := 1
	if rawPage != "" {
		page, err = strconv.Atoi(rawPage)
		if err != nil {
			c.Status(fiber.StatusBadRequest)
			return c.JSON(fiber.Map{"error": "Query cannot be parsed."})
		}
	}

	rawDatetime := c.Query("datetime")
	datetime := 0
	if rawDatetime != "" {
		datetime, err = strconv.Atoi(rawDatetime)
		if err != nil {
			c.Status(fiber.StatusBadRequest)
			return c.JSON(fiber.Map{"error": "Query cannot be parsed."})
		}
	}

	var count int64
	var isNext string
	database.Conn.Model(&models.Record{}).Where("user_id = ? AND updated_at > ?", claims["uid"], datetime).Count(&count).Limit(50).Offset((page - 1) * 50).Find(&records)
	if count > int64(page*50) {
		isNext = "1"
	} else {
		isNext = "0"
	}
	c.Append("Is-Next", isNext)

	return c.JSON(records)
}

func updateRecords(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	uid := uint(claims["uid"].(float64))

	records := []models.Record{}
	if err := c.BodyParser(&records); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	for _, record := range records {
		record.UserID = uid
		prevRecord := models.Record{UserID: uid, ID: record.ID, Driver: record.Driver}

		// check if there is a previous record
		result := database.Conn.Limit(1).Find(&prevRecord)
		if result.RowsAffected == 1 {
			// only keep the latest one
			if prevRecord.Datetime < record.Datetime {
				database.Conn.Save(&record)
			}
		} else {
			database.Conn.Create(&record)
		}
	}

	c.Status(fiber.StatusAccepted)
	return getRecords(c)
}

func resetRecords(c *fiber.Ctx) error {
	// get info
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	driver := c.Query("driver")
	id := c.Query("id")

	if driver == "" || id == "" {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": `\"driver\" or \"id\" are missing.`})
	}

	// get the record
	record := models.Record{
		UserID: uint(claims["uid"].(float64)),
		Driver: driver,
		ID:     id,
	}
	database.Conn.First(&record)

	// set the record to nil and save
	record.ChapterID = nil
	record.ChapterTitle = nil
	record.Page = nil
	database.Conn.Save(&record)

	c.Status(fiber.StatusNoContent)
	return nil

}
