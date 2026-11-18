package handlers

import (
	"encoding/json"
	"log/slog"
	"net/http"

	"tomsherlock.space/backend/internal/config"
	"tomsherlock.space/backend/internal/store"
)

// Handler carries the dependencies shared by every HTTP handler.
type Handler struct {
	cfg    config.Config
	store  *store.Store
	logger *slog.Logger
}

// New constructs a Handler.
func New(cfg config.Config, st *store.Store, logger *slog.Logger) *Handler {
	return &Handler{cfg: cfg, store: st, logger: logger}
}

// Healthz is a liveness probe: the process is up.
func (h *Handler) Healthz(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

// Readyz is a readiness probe: the process can reach its dependencies.
func (h *Handler) Readyz(w http.ResponseWriter, r *http.Request) {
	if err := h.store.Ping(r.Context()); err != nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"status": "unavailable"})
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "ready"})
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func writeError(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, map[string]string{"error": msg})
}
