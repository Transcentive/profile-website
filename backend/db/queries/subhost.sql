-- name: ListSubhosts :many
SELECT * FROM subhosts ORDER BY slug;

-- name: GetSubhost :one
SELECT * FROM subhosts WHERE slug = $1;

-- name: UpsertSubhost :one
INSERT INTO subhosts (slug, name, subdomain, upstream, enabled)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (slug) DO UPDATE
SET name = EXCLUDED.name,
    subdomain = EXCLUDED.subdomain,
    upstream = EXCLUDED.upstream,
    enabled = EXCLUDED.enabled
RETURNING *;
