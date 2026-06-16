package handlers

import (
	"crypto/subtle"
	"net/http"
	"strings"

	"tomsherlock.space/backend/internal/dbgen"
)

// RequireAdmin gates a route group behind a constant-time bearer-token check.
func (h *Handler) RequireAdmin(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")
		if token == "" || subtle.ConstantTimeCompare([]byte(token), []byte(h.cfg.AdminToken)) != 1 {
			writeError(w, http.StatusUnauthorized, "unauthorized")
			return
		}
		next.ServeHTTP(w, r)
	})
}

// ListContact returns the most recent contact messages (admin-only).
func (h *Handler) ListContact(w http.ResponseWriter, r *http.Request) {
	msgs, err := h.store.Queries.ListContactMessages(r.Context(), dbgen.ListContactMessagesParams{
		Limit:  100,
		Offset: 0,
	})
	if err != nil {
		h.logger.Error("list contact", "err", err)
		writeError(w, http.StatusInternalServerError, "could not load messages")
		return
	}
	writeJSON(w, http.StatusOK, msgs)
}

// ListSubhosts returns the registered subhosted apps (admin-only).
func (h *Handler) ListSubhosts(w http.ResponseWriter, r *http.Request) {
	hosts, err := h.store.Queries.ListSubhosts(r.Context())
	if err != nil {
		h.logger.Error("list subhosts", "err", err)
		writeError(w, http.StatusInternalServerError, "could not load subhosts")
		return
	}
	writeJSON(w, http.StatusOK, hosts)
}
