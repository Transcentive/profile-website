# Backend — architecture & target stack

The frontend of this site was built with Claude Design and is largely complete
(hand-authored static HTML/CSS/JS: `index.html`, the five `track-*.html` pages,
shared `styles.css` + `nav.js`). Work is now shifting to the **backend**.

## Decisions

| Concern | Choice |
|---|---|
| Backend language / runtime | **Go** |
| HTTP stack | **stdlib `net/http` + go-chi/chi v5** |
| Database | **PostgreSQL** via **pgx v5 + sqlc** (type-safe codegen, no ORM) |
| Backend location | **Same repo, in a `backend/` directory** (alongside the static frontend) |
| Web server | **Nginx** (TLS edge + reverse proxy) |
| Subhosting | **Subdomain-based**, each mini-app reverse-proxied by Nginx to its own service |
| OS | **Linux / Ubuntu** |
| Host | **DigitalOcean** |

## Capabilities

1. Serve the static site (Nginx serves files; Go handles dynamic routes).
2. Contact form / messaging.
3. Content / CMS API.
4. Admin + analytics.
5. Subhost mini-apps/web-tools on subdomains (e.g. the brewery **NAM.LU.DIN** and
   **Mighty Queue** apps referenced on `track-ai.html`).

## Goal

A useful, accessible, aesthetic, navigable, comprehensible website.

## Scaffolding

The **`site-backend`** skill provides the scaffolding, tools, and conventions for
the backend. It lives in this repository at `.claude/skills/site-backend/`, with
its companions `provision-db` and `backend-stack`, so it loads only when working
on this site (moved from `~/.claude/skills/` on November 18, 2026, because its
stack, chi and sqlc, conflicts with The Mighty Queue and PhoenixEvent). It bundles a verified Go template, a `scaffold_backend.py` generator, a
`new_subhost.py` Nginx-config generator, and references covering architecture, the
pgx+sqlc database workflow, subhosting, and DigitalOcean deployment. Run it from
the repo root to create `backend/` here:

```bash
python3 .claude/skills/site-backend/scripts/scaffold_backend.py
```

The module path defaults to `tomsherlock.space/backend` (override with `--module`).
