# Database: PostgreSQL + pgx + sqlc

The data layer is **pgx v5** (driver/pool) plus **sqlc** (type-safe Go generated
from plain SQL). There is no ORM. Queries are written in SQL; sqlc generates the
Go that runs them, checked at compile time.

## The loop for adding/changing data access

1. **Schema change?** Add a new migration pair under `db/migrations/`:
   `0002_add_x.up.sql` and `0002_add_x.down.sql` (zero-padded, golang-migrate
   naming). Keep `up` and `down` symmetric.
2. **Write the query** in the relevant `db/queries/*.sql` file with an sqlc
   annotation:
   ```sql
   -- name: GetThing :one      -- one row   → (Thing, error)
   -- name: ListThings :many   -- many rows → ([]Thing, error)
   -- name: DeleteThing :exec  -- no rows   → error
   ```
3. **Generate:** `make sqlc` (runs `sqlc generate`). This rewrites
   `internal/dbgen/`. NEVER edit those files by hand.
4. **Use it** from a handler via `h.store.Queries.GetThing(ctx, arg)`.
5. **Build:** `go build ./...` — a mismatch between SQL and Go is a compile error.

## Naming → Go mapping (sqlc)

- Table `content_blocks` → struct `ContentBlock`; column `created_at` → `CreatedAt`.
- A query with >1 parameter generates a `<QueryName>Params` struct.
- `RETURNING *` returns the table's row struct.
- `count(*) AS total` → field `Total int64`.

## Type choices that keep handlers clean

| SQL                          | Go (sqlc, pgx/v5)        | Note                         |
|------------------------------|--------------------------|------------------------------|
| `TEXT NOT NULL`              | `string`                 | preferred for optional text via `DEFAULT ''` |
| `BIGSERIAL` / `BIGINT`       | `int64`                  |                              |
| `BOOLEAN NOT NULL`           | `bool`                   |                              |
| `JSONB NOT NULL`             | `[]byte`                 | wrap with `json.RawMessage`  |
| `TIMESTAMPTZ NOT NULL`       | `pgtype.Timestamptz`     | construct `{Time: t, Valid: true}` |

Avoid nullable columns where a sensible non-null default exists — it removes a
layer of `pgtype.*` wrappers from the handler code.

## Migrations in production

`make migrate-up` / `make migrate-down` shell out to **golang-migrate**:

```bash
# install once on the droplet
curl -sSL https://github.com/golang-migrate/migrate/releases/latest/download/migrate.linux-amd64.tar.gz | tar xz
sudo mv migrate /usr/local/bin/

export DATABASE_URL='postgres://site:...@127.0.0.1:5432/site?sslmode=disable'
make migrate-up
```

sqlc reads the same `db/migrations/` dir for the schema (it applies only the
`.up.sql` files), so the schema sqlc sees always matches what migrate applies.

## Local Postgres setup

```bash
sudo -u postgres psql <<'SQL'
CREATE ROLE site WITH LOGIN PASSWORD 'changeme';
CREATE DATABASE site OWNER site;
SQL
```
Then set `DATABASE_URL` in `.env` and run `make migrate-up`.
