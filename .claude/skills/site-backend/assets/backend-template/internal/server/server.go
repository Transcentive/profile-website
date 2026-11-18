package server

import (
	"log/slog"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"

	"MODULE_PATH/internal/config"
	"MODULE_PATH/internal/handlers"
	"MODULE_PATH/internal/store"
)

// New builds the HTTP handler: middleware stack + route table.
//
// The Go backend owns the dynamic surface (API + admin) for the MAIN site only.
// Static files are served by Nginx, and subhosted mini-apps are reverse-proxied
// by Nginx at their own subdomains — they never pass through this router.
func New(cfg config.Config, st *store.Store, logger *slog.Logger) http.Handler {
	r := chi.NewRouter()

	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(requestLogger(logger))
	r.Use(middleware.Recoverer)
	r.Use(securityHeaders)
	r.Use(cors(cfg.AllowOrigin))

	h := handlers.New(cfg, st, logger)

	// Liveness / readiness probes (used by systemd healthchecks and Nginx).
	r.Get("/healthz", h.Healthz)
	r.Get("/readyz", h.Readyz)

	// Public API consumed by the static frontend.
	r.Route("/api", func(r chi.Router) {
		r.Post("/contact", h.CreateContact)
		r.Get("/content/{slug}", h.GetContent)
		r.Post("/events", h.RecordEvent)
	})

	// Authenticated admin surface (token in Authorization: Bearer ...).
	r.Route("/admin", func(r chi.Router) {
		r.Use(h.RequireAdmin)
		r.Get("/contact", h.ListContact)
		r.Put("/content/{slug}", h.UpsertContent)
		r.Get("/analytics/summary", h.AnalyticsSummary)
		r.Get("/subhosts", h.ListSubhosts)
	})

	return r
}
