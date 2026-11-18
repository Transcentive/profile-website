---
name: backend-stack
description: >-
  Stand up a complete local backend in one chained run: scaffold the Go backend
  (site-backend skill) AND provision its local PostgreSQL database (provision-db
  skill), passing the scaffolded backend straight into the DB setup. Use when the
  user wants the whole backend + database ready to run on localhost in one step —
  "set up the full backend", "scaffold and wire up the database", "give me a
  runnable backend stack". Chains the site-backend and provision-db skills.
---

# backend-stack

One command that produces a **runnable local backend stack** by chaining two
skills:

1. **`site-backend`** — scaffolds `backend/` (Go + chi + pgx/sqlc), then builds it.
2. **`provision-db`** — creates the local Postgres DB + role, applies the
   migrations, and writes `.env`.

The handoff is automatic: the directory created in step 1 is passed as the
`--backend-dir` of step 2, so the migrations and `.env` land in exactly the tree
that was just scaffolded. No manual copying of paths or secrets.

## When to use this vs. the individual skills

- **Fresh project, want it runnable now →** `backend-stack` (this skill).
- **Only need the code / no DB yet →** `site-backend` alone.
- **Backend already scaffolded, just need a local DB →** `provision-db` alone.

## Prerequisites

- `go` and `sqlc` on `PATH` (for the scaffold + build).
- A local PostgreSQL you can administer (Homebrew/macOS: `brew services start
  postgresql@14`), with `psql` on `PATH`.

## Run it

From the project root (where `backend/` should be created):

```bash
python3 .claude/skills/backend-stack/scripts/up.py \
  --domain tomsherlock.space \
  --site-root /var/www/tomsherlock.space
```

Defaults: module `tomsherlock.space/backend`, target `backend/`, db name/user
`site`. `--domain` also becomes the CORS origin (`https://<domain>`) in `.env`.

### Flags

- `--module PATH` — Go module path (default `tomsherlock.space/backend`).
- `--domain` / `--site-root` — fill the Nginx config in step 1; `--domain` also
  sets the `.env` CORS origin.
- `--target DIR` — backend output dir (default `backend`).
- `--db-name` / `--db-user` — database + role names (default `site`).
- `--allow-origin URL` — override the CORS origin written to `.env`.
- `--force` — overwrite an existing `backend/` **and** regenerate `.env`.

The chain stops if either step fails (it won't try to migrate a backend that
didn't scaffold). Both underlying steps are idempotent, so re-running is safe.

## After it finishes

```bash
cd backend && set -a && source .env && set +a && make run
curl localhost:8080/healthz    # liveness
curl localhost:8080/readyz     # confirms DB connectivity
```
