-- name: RecordEvent :exec
INSERT INTO analytics_events (kind, path, referrer, subhost, session_id, user_agent)
VALUES ($1, $2, $3, $4, $5, $6);

-- name: CountEventsByKind :many
SELECT kind, count(*) AS total
FROM analytics_events
WHERE created_at >= $1
GROUP BY kind
ORDER BY total DESC;
