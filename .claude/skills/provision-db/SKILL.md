---
name: provision-db
description: >-
  Provision a local PostgreSQL database for testing a backend: create the
  database + login role, apply the schema migrations (db/migrations/*.up.sql),
  and write a ready-to-run .env (DATABASE_URL + generated ADMIN_TOKEN). Use when
  setting up or resetting a local database for a backend, "create a database and
  user", "set up the local DB", "apply the migrations", or getting a scaffolded
  backend runnable on localhost. Standalone; pairs with the site-backend and
  backend-stack skills.
---

# provision-db

Stand up a **local PostgreSQL** database so a backend can run and be tested on
localhost. It performs three steps, idempotently (safe to re-run):

1. **Create the role + database** — a `LOGIN` role and a database it owns, if
   they don't already exist.
2. **Apply the schema** — runs every `db/migrations/*.up.sql` in the backend,
   in filename order (skipped if the schema is already present).
3. **Write `.env`** — fills `DATABASE_URL` and a freshly generated `ADMIN_TOKEN`
   from the backend's `.env.example`, so the server starts with no further edits.

This skill only touches the **database side**. It does not scaffold or build the
backend code — that's the `site-backend` skill. To do both at once, use the
`backend-stack` skill, which chains them.

## Prerequisites

- A local PostgreSQL you can administer (Homebrew/macOS: `brew services start
  postgresql@14`; your OS user is the superuser). `psql` must be on `PATH`.
- A backend dir containing `db/migrations/*.up.sql` and (ideally) `.env.example`
  — i.e. a tree produced by the `site-backend` skill.

## Run it

From the project root (so `backend/` is the default target):

```bash
python3 .claude/skills/provision-db/scripts/setup_local_db.py
```

Defaults: `--backend-dir backend`, db name/user `site`, host `127.0.0.1:5432`.
On success it prints the `DATABASE_URL` and the exact command to start the server.

### Useful flags

- `--backend-dir DIR` — backend holding `db/migrations` and receiving `.env`
  (default `backend`).
- `--db-name` / `--db-user` — names to create (default `site` / `site`).
- `--allow-origin URL` — CORS origin written into `.env` (e.g.
  `https://tomsherlock.space`).
- `--force` — regenerate `.env` even if one exists (otherwise it's left intact).
- `--force-migrate` — re-apply migrations even if tables already exist.
- `--superuser ROLE` / `--maintenance-db DB` — override the admin connection if
  your local Postgres isn't peer-authenticated as your OS user.

## Idempotency & safety

- Re-running is safe: an existing role/database is reused (password re-synced),
  migrations are skipped when the schema is already there, and an existing `.env`
  is preserved unless `--force`.
- Secrets are **reused** from an existing `.env` when present (so the DB password
  stays in sync), otherwise generated with `secrets.token_hex`.
- `.env` is gitignored by the backend template — never commit it.

## Run the server afterward

`make run` does **not** auto-load `.env`; source it first:

```bash
cd backend && set -a && source .env && set +a && make run
# then, in another shell:
curl localhost:8080/healthz   # liveness
curl localhost:8080/readyz    # confirms DB connectivity
```
