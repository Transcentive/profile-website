# Subhosting mini-apps (subdomain reverse-proxy)

The portfolio site doubles as a host for independent web tools — e.g.
**NAM.LU.DIN** (the brewery oversight system, Go + Flutter) and **The Mighty
Queue** — referenced as live specimens on `track-ai.html`.

## Model: subdomain → Nginx reverse-proxy → independent service

Each sub-app:
- runs as its **own service** (its own process/port, any language/stack),
  managed by its own systemd unit;
- is reached at its **own subdomain** (`brewery.tomsherlock.space`);
- is wired in purely at the **Nginx** layer. It never passes through the Go
  backend's router. The Go backend only records analytics about it (the
  `subhosts` table + the `subhost` field on `analytics_events`).

This keeps sub-apps fully decoupled: deploy, restart, or break one without
touching the main site or the others.

## Add a sub-app

1. **Run the service** on a free local port (e.g. `127.0.0.1:9001`) under its own
   systemd unit. Bind to loopback only — Nginx is the public edge.
2. **Generate the Nginx config:**
   ```bash
   python3 .claude/skills/site-backend/scripts/new_subhost.py \
     --slug brewery --subdomain brewery.tomsherlock.space --upstream 127.0.0.1:9001
   ```
   This writes `backend/deploy/nginx/brewery.conf`.
3. **DNS:** add an `A` record for the subdomain → droplet IP. A wildcard
   `*.tomsherlock.space` A record covers all future sub-apps at once.
4. **Install + reload:**
   ```bash
   sudo cp backend/deploy/nginx/brewery.conf /etc/nginx/sites-available/brewery.conf
   sudo ln -s /etc/nginx/sites-available/brewery.conf /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```
5. **TLS:** `sudo certbot --nginx -d brewery.tomsherlock.space` (or one wildcard
   cert via DNS-01 — see deployment.md).
6. **Register it** (optional, for the admin/analytics view): insert a row into
   `subhosts` (`UpsertSubhost`) so it shows under `GET /admin/subhosts`.

## Notes

- The generated config forwards WebSocket/SSE upgrade headers, so Flutter-web and
  live-demo sockets work through the proxy.
- Keep one `*.conf` per app; deleting a sub-app = remove its file + unit + DNS.
- Wildcard DNS + a wildcard TLS cert means new sub-apps need no DNS/cert change —
  only steps 1, 2, 4.
