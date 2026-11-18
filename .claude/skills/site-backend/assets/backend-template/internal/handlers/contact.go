package handlers

import (
	"encoding/json"
	"net/http"
	"strings"

	"MODULE_PATH/internal/dbgen"
)

type contactRequest struct {
	Name    string `json:"name"`
	Email   string `json:"email"`
	Subject string `json:"subject"`
	Body    string `json:"body"`
}

// CreateContact validates and stores a contact-form submission.
func (h *Handler) CreateContact(w http.ResponseWriter, r *http.Request) {
	var req contactRequest
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid JSON body")
		return
	}

	req.Name = strings.TrimSpace(req.Name)
	req.Email = strings.TrimSpace(req.Email)
	req.Subject = strings.TrimSpace(req.Subject)
	req.Body = strings.TrimSpace(req.Body)
	if req.Name == "" || !strings.Contains(req.Email, "@") || req.Body == "" {
		writeError(w, http.StatusBadRequest, "name, a valid email, and body are required")
		return
	}

	msg, err := h.store.Queries.CreateContactMessage(r.Context(), dbgen.CreateContactMessageParams{
		Name:      req.Name,
		Email:     req.Email,
		Subject:   req.Subject,
		Body:      req.Body,
		SourceIp:  realIP(r),
		UserAgent: r.UserAgent(),
	})
	if err != nil {
		h.logger.Error("create contact", "err", err)
		writeError(w, http.StatusInternalServerError, "could not save message")
		return
	}

	writeJSON(w, http.StatusCreated, map[string]any{"id": msg.ID, "received": true})
}

// realIP extracts the client IP, trusting the proxy headers Nginx sets.
func realIP(r *http.Request) string {
	if ip := strings.TrimSpace(r.Header.Get("X-Real-IP")); ip != "" {
		return ip
	}
	if fwd := r.Header.Get("X-Forwarded-For"); fwd != "" {
		return strings.TrimSpace(strings.Split(fwd, ",")[0])
	}
	host := r.RemoteAddr
	if i := strings.LastIndex(host, ":"); i != -1 {
		host = host[:i]
	}
	return host
}
