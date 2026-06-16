-- name: CreateContactMessage :one
INSERT INTO contact_messages (name, email, subject, body, source_ip, user_agent)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING *;

-- name: ListContactMessages :many
SELECT * FROM contact_messages
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: MarkContactHandled :exec
UPDATE contact_messages SET handled = TRUE WHERE id = $1;
