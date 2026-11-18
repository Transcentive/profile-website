---
name: site-backend
description: >-
  Scaffold and build a Go backend for a website. Use when working on a backend/
  directory, the server API, database, or deployment of a site — e.g. scaffolding
  a Go backend, adding an API or admin endpoint, a contact form, CMS content,
  analytics, a database table or query (PostgreSQL via pgx + sqlc), subhosting a
  mini-app/web-tool on a subdomain, or deploying to an Ubuntu droplet on
  DigitalOcean with Nginx. Stack: Go (net/http + chi), pgx + sqlc, PostgreSQL,
  Nginx, Ubuntu, DigitalOcean.
---

# site-backend

Build a Go backend for a website. This skill scaffolds and grows the backend in a
`backend/` directory of the project you're working in (alongside a static
frontend, if there is one).

## Stack (fixed — do not substitute)

- **Go** with stdlib `net/http` + **go-chi/chi v5** for routing/middleware.
- **PostgreSQL** via **pgx v5** + **sqlc** (type-safe Go generated from SQL; no ORM).
- **Nginx** as the TLS edge and reverse proxy; **Ubuntu** host on **DigitalOcean**.

## Capabilities this backend provides

1. Serve the static site (via Nginx; Go handles dynamic routes).
2. Contact form / messaging (`POST /api/contact`).
3. Content/CMS API (`GET /api/content/{slug}`, admin upsert).
4. Admin + analytics (token-gated `/admin/*`, event recording).
5. **Subhost mini-apps** on subdomains via Nginx reverse-proxy (brewery, queue, …).

## First: is the backend scaffolded yet?

Check for `backend/go.mod` in the repo.

- **Not scaffolded →** run the scaffolder (below), then build.
- **Already scaffolded →** make the change directly using the conventions in
  `references/architecture.md`.

## Scaffold the backend (one time)

Run the bundled script from the root of the project you want the backend in:

```bash
python3 .claude/skills/site-backend/scripts/scaffold_backend.py
```

The Go module path defaults to `tomsherlock.space/backend`; override it for a
different project with `--module <path>` (e.g. `--module example.com/backend`).
It copies the template into `backend/`, renames `*.tmpl` (e.g. `go.mod.tmpl` →
`go.mod`), substitutes the module path, then runs `sqlc generate`, `go mod tidy`,
and `go build ./...`. Flags: `--target` (output dir), `--domain` / `--site-root`
(fill Nginx placeholders), `--no-build`, `--force`. Requires `go` and `sqlc`
installed; without `sqlc`, pass `--no-build` and generate later.

The generated tree, conventions, and where each capability lives are documented
in **`references/architecture.md`** — read it before editing the backend.

## Common tasks

**Add an API or admin endpoint**
1. Add the route in `backend/internal/server/server.go` (public → `/api`,
   privileged → `/admin`, which is behind `RequireAdmin`).
2. Add the handler method on `*handlers.Handler` in the matching
   `backend/internal/handlers/*.go`. Keep it thin: decode + validate → call a
   `store.Queries.*` method → `writeJSON`/`writeError`.

**Add or change database access** — see **`references/database.md`**. Summary:
edit `backend/db/queries/*.sql` (and a migration in `db/migrations/` if the
schema changes), run `make sqlc`, then use the generated method. Never hand-edit
`internal/dbgen/`.

**Subhost a mini-app on a subdomain** — see **`references/subhosting.md`**.
Generate the Nginx config with:
```bash
python3 .claude/skills/site-backend/scripts/new_subhost.py \
  --slug brewery --subdomain brewery.tomsherlock.space --upstream 127.0.0.1:9001
```

**Deploy / operate on the droplet** — see **`references/deployment.md`** (Postgres
setup, systemd unit, Nginx install, certbot TLS, update workflow).

## References

- `references/architecture.md` — system diagram, `backend/` layout, conventions,
  capability map. **Start here when editing the backend.**
- `references/database.md` — pgx + sqlc workflow, type mappings, migrations.
- `references/subhosting.md` — subdomain reverse-proxy model, adding a sub-app.
- `references/deployment.md` — Ubuntu/DigitalOcean: Nginx, systemd, TLS, updates.

## Conventions (do not violate)

- Routing only in `server.go`; handlers stay thin; all SQL via sqlc on
  `h.store.Queries`. Config is env-only (`DATABASE_URL`, `ADMIN_TOKEN` required).
- The Go backend serves the **main site's** dynamic routes only. Subhosted apps
  are independent services wired in at the **Nginx** layer — never proxied
  through the Go router.
- Log internal errors; return generic messages to clients.
