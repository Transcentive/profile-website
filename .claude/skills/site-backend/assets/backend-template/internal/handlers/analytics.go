package handlers

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/jackc/pgx/v5/pgtype"

	"MODULE_PATH/internal/dbgen"
)

type eventRequest struct {
	Kind      string `json:"kind"`
	Path      string `json:"path"`
	Referrer  string `json:"referrer"`
	Subhost   string `json:"subhost"`
	SessionID string `json:"session_id"`
}

// RecordEvent stores a lightweight analytics event (pageview, cv_download, ...).
func (h *Handler) RecordEvent(w http.ResponseWriter, r *http.Request) {
	var req eventRequest
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<18)).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid JSON body")
		return
	}
	if req.Kind == "" {
		req.Kind = "pageview"
	}

	err := h.store.Queries.RecordEvent(r.Context(), dbgen.RecordEventParams{
		Kind:      req.Kind,
		Path:      req.Path,
		Referrer:  req.Referrer,
		Subhost:   req.Subhost,
		SessionID: req.SessionID,
		UserAgent: r.UserAgent(),
	})
	if err != nil {
		h.logger.Error("record event", "err", err)
		writeError(w, http.StatusInternalServerError, "could not record event")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

// AnalyticsSummary returns event counts by kind over the last 30 days (admin-only).
func (h *Handler) AnalyticsSummary(w http.ResponseWriter, r *http.Request) {
	since := pgtype.Timestamptz{Time: time.Now().AddDate(0, 0, -30), Valid: true}
	rows, err := h.store.Queries.CountEventsByKind(r.Context(), since)
	if err != nil {
		h.logger.Error("analytics summary", "err", err)
		writeError(w, http.StatusInternalServerError, "could not load analytics")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"since": since.Time, "by_kind": rows})
}
