package store

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"

	"tomsherlock.space/backend/internal/dbgen"
)

// Store wraps the pgx connection pool and the sqlc-generated query set.
type Store struct {
	pool    *pgxpool.Pool
	Queries *dbgen.Queries
}

// New opens a pooled connection to PostgreSQL and verifies it with a ping.
func New(ctx context.Context, databaseURL string) (*Store, error) {
	pool, err := pgxpool.New(ctx, databaseURL)
	if err != nil {
		return nil, err
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, err
	}
	return &Store{pool: pool, Queries: dbgen.New(pool)}, nil
}

// Ping checks database connectivity (used by the readiness probe).
func (s *Store) Ping(ctx context.Context) error { return s.pool.Ping(ctx) }

// Close releases the connection pool.
func (s *Store) Close() { s.pool.Close() }
