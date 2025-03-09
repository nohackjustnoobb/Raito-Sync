package main

import (
	"Raito-Sync/database"
	"Raito-Sync/routes"
	"os"

	"github.com/gofiber/contrib/fiberzerolog"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

const VERSION = "1.0.0"

func main() {
	// setup fiber app
	app := fiber.New(fiber.Config{
		Prefork: true,
		AppName: "Raito-Sync v" + VERSION,
	})

	// setup logging
	logger := log.Output(zerolog.ConsoleWriter{Out: os.Stderr})
	app.Use(fiberzerolog.New(fiberzerolog.Config{
		Logger: &logger,
	}))

	// setup database
	database.Setup()

	// setup cors middleware
	app.Use(cors.New(cors.Config{ExposeHeaders: "Is-Next"}))

	// setup handlers
	app.Get("/", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"version": VERSION})
	})
	routes.SetupUserRoutes(app)
	routes.SetupSyncRoutes(app)

	app.Listen(":3000")
}
