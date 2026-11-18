package config

import (
	"fmt"
	"os"
)

// Config holds all runtime configuration, sourced from environment variables.
type Config struct {
	Env         string
	ListenAddr  string
	DatabaseURL string
	AdminToken  string
	AllowOrigin string
}

// Load reads configuration from the environment and validates required fields.
func Load() (Config, error) {
	cfg := Config{
		Env:         getenv("APP_ENV", "development"),
		ListenAddr:  getenv("LISTEN_ADDR", "127.0.0.1:8080"),
		DatabaseURL: os.Getenv("DATABASE_URL"),
		AdminToken:  os.Getenv("ADMIN_TOKEN"),
		AllowOrigin: getenv("ALLOW_ORIGIN", "*"),
	}
	if cfg.DatabaseURL == "" {
		return cfg, fmt.Errorf("DATABASE_URL is required")
	}
	if cfg.AdminToken == "" {
		return cfg, fmt.Errorf("ADMIN_TOKEN is required")
	}
	return cfg, nil
}

func getenv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
