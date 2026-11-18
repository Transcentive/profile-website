package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"

	"MODULE_PATH/internal/dbgen"
)

// GetContent returns a single PUBLISHED content block as JSON.
func (h *Handler) GetContent(w http.ResponseWriter, r *http.Request) {
	slug := chi.URLParam(r, "slug")
	block, err := h.store.Queries.GetPublishedContent(r.Context(), slug)
	if err != nil {
		writeError(w, http.StatusNotFound, "not found")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"slug":  block.Slug,
		"title": block.Title,
		"body":  json.RawMessage(block.Body),
	})
}

type contentRequest struct {
	Title     string          `json:"title"`
	Body      json.RawMessage `json:"body"`
	Published bool            `json:"published"`
}

// UpsertContent creates or replaces a content block (admin-only).
func (h *Handler) UpsertContent(w http.ResponseWriter, r *http.Request) {
	slug := chi.URLParam(r, "slug")
	var req contentRequest
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid JSON body")
		return
	}
	if len(req.Body) == 0 {
		req.Body = json.RawMessage("{}")
	}

	block, err := h.store.Queries.UpsertContent(r.Context(), dbgen.UpsertContentParams{
		Slug:      slug,
		Title:     req.Title,
		Body:      []byte(req.Body),
		Published: req.Published,
	})
	if err != nil {
		h.logger.Error("upsert content", "err", err)
		writeError(w, http.StatusInternalServerError, "could not save content")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"slug": block.Slug, "updated": true})
}
