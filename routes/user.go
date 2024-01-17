package routes

import (
	"Raito-Sync/database"
	"Raito-Sync/models"
	"encoding/json"
	"os"
	"regexp"
	"time"
	"unicode"

	jwtware "github.com/gofiber/contrib/jwt"
	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
	"github.com/matthewhartstonge/argon2"
)

var (
	argon       = argon2.DefaultConfig()
	SecretKey   string
	RegisterKey *string = nil
)

type Config struct {
	SecretKey   string  `json:"secretKey"`
	RegisterKey *string `json:"registerKey,omitempty"`
}

func SetupUserRoutes(app *fiber.App) {
	// read config json
	content, err := os.ReadFile("config.json")
	if err != nil {
		panic("Fail to open config.json")
	}

	var payload Config
	err = json.Unmarshal(content, &payload)
	if err != nil {
		panic("Fail to parse config.json")
	}

	SecretKey = payload.SecretKey
	RegisterKey = payload.RegisterKey

	// routes
	app.Post("/create", createUser)
	app.Post("/token", obtainToken)

	// setup middleware
	app.Use(jwtware.New(jwtware.Config{
		SigningKey: jwtware.SigningKey{
			JWTAlg: jwtware.HS512,
			Key:    []byte(SecretKey),
		},
	}))

	app.Get("/me", myInfo)
	app.Post("/me", changePassword)

	app.Post("/clear", clearAccount)
}

type RegistrationInfo struct {
	Email    string `json:"email" xml:"email" form:"email"`
	Password string `json:"password" xml:"password" form:"password"`
	Key      string `json:"key,omitempty" xml:"key,omitempty" form:"key,omitempty"`
}

func createUser(c *fiber.Ctx) error {
	// get registration information
	info := new(RegistrationInfo)
	if err := c.BodyParser(info); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	// check register key
	if RegisterKey != nil && *RegisterKey != "" && *RegisterKey != info.Key {
		c.Status(fiber.StatusUnauthorized)
		return c.JSON(fiber.Map{"error": "Invalid register key."})
	}

	// check email
	if !verifyEmail(info.Email) {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Email is not valid."})
	}

	// check password
	if !verifyPassword(info.Password) {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Passwords must contain at least eight characters, one letter and one number."})
	}

	encoded, err := argon.HashEncoded([]byte(info.Password))
	if err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Fail to hash password."})
	}

	user := models.User{
		Email:    info.Email,
		Password: string(encoded),
	}
	result := database.Conn.Create(&user)
	if result.Error != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "An unexpected error occurred when trying to create user."})
	}

	return c.JSON(user)
}

type LoginInfo struct {
	Email    string `json:"email" xml:"email" form:"email"`
	Password string `json:"password" xml:"password" form:"password"`
}

func obtainToken(c *fiber.Ctx) error {
	info := new(LoginInfo)
	if err := c.BodyParser(info); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	// get the user from the database
	user := new(models.User)
	result := database.Conn.Where("email = ?", info.Email).First(user)
	if result.Error != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": `\"email\" or \"password\" are incorrect.`})
	}

	// check if the password is correct
	ok, err := argon2.VerifyEncoded([]byte(info.Password), []byte(user.Password))
	if !ok || err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": `\"email\" or \"password\" are incorrect.`})
	}

	// generate the token
	claims := jwt.MapClaims{
		"iss": "RaitoManga",
		"iat": time.Now().UnixMilli(),
		"uid": user.ID,
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS512, claims)

	// sign the token
	signed, err := token.SignedString([]byte(SecretKey))
	if err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "An unexpected error occurred when trying to sign the token."})
	}

	return c.JSON(fiber.Map{"token": signed})
}

func myInfo(c *fiber.Ctx) error {
	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	user := new(models.User)
	database.Conn.First(user, claims["uid"].(float64))

	return c.JSON(user)
}

type ChangePasswordInfo struct {
	OldPassword string `json:"oldPassword" xml:"oldPassword" form:"oldPassword"`
	NewPassword string `json:"newPassword" xml:"newPassword" form:"newPassword"`
}

func changePassword(c *fiber.Ctx) error {
	info := new(ChangePasswordInfo)
	if err := c.BodyParser(info); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	user := new(models.User)
	database.Conn.First(user, claims["uid"].(float64))

	// check if the password is correct
	ok, err := argon2.VerifyEncoded([]byte(info.OldPassword), []byte(user.Password))
	if !ok || err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Old password is incorrect."})
	}

	// check password
	if !verifyPassword(info.NewPassword) {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Passwords must contain at least eight characters, one letter and one number."})
	}

	// hash the password
	encoded, err := argon.HashEncoded([]byte(info.NewPassword))
	if err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Fail to hash password."})
	}

	// update the database
	user.Password = string(encoded)
	database.Conn.Save(user)

	return c.JSON(user)
}

type clearAccountInfo struct {
	Password string `json:"password"`
}

func clearAccount(c *fiber.Ctx) error {
	info := new(clearAccountInfo)
	if err := c.BodyParser(info); err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Body cannot be parsed."})
	}

	// get the user
	claims := c.Locals("user").(*jwt.Token).Claims.(jwt.MapClaims)
	user := new(models.User)
	database.Conn.First(user, claims["uid"].(float64))

	// check if the password is correct
	ok, err := argon2.VerifyEncoded([]byte(info.Password), []byte(user.Password))
	if !ok || err != nil {
		c.Status(fiber.StatusBadRequest)
		return c.JSON(fiber.Map{"error": "Password is incorrect."})
	}

	// delete all the data
	database.Conn.Where("user_id = ?", user.ID).Delete(&models.Manga{})
	database.Conn.Where("user_id = ?", user.ID).Delete(&models.Record{})

	c.Status(fiber.StatusNoContent)
	return nil

}

func verifyEmail(email string) bool {
	re := regexp.MustCompile(`(?:[a-z0-9!#$%&'*+\=?^_` + "`" + `{|}~-]+(?:\.[a-z0-9!#$%&'*+\=?^_` + "`" + `{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])`)
	return re.MatchString(email)
}

func verifyPassword(password string) bool {
	var count int
	var number bool
	var letter bool

	for _, c := range password {
		switch {
		case unicode.IsDigit(c):
			number = true
		case unicode.IsLetter(c):
			letter = true
		}
		count++
	}

	return count >= 8 && number && letter
}
