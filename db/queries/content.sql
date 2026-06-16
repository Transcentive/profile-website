-- name: GetPublishedContent :one
SELECT * FROM content_blocks WHERE slug = $1 AND published = TRUE;

-- name: GetContent :one
SELECT * FROM content_blocks WHERE slug = $1;

-- name: ListContent :many
SELECT * FROM content_blocks ORDER BY slug;

-- name: UpsertContent :one
INSERT INTO content_blocks (slug, title, body, published, updated_at)
VALUES ($1, $2, $3, $4, now())
ON CONFLICT (slug) DO UPDATE
SET title = EXCLUDED.title,
    body = EXCLUDED.body,
    published = EXCLUDED.published,
    updated_at = now()
RETURNING *;
