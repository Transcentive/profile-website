# Deployment: Ubuntu droplet on DigitalOcean

For tomsherlock.space, the Deploying section of `CLAUDE.md` governs: its paths
and commands replace the general ones below.

Target: a single Ubuntu droplet running Nginx (edge), the Go backend, PostgreSQL,
and any sub-app services — all behind systemd.

## 1. Provision

- Create an Ubuntu LTS droplet; add an `A` record `tomsherlock.space` → droplet IP
  (and `www`, plus a wildcard `*.tomsherlock.space` for sub-apps).
- Create a non-root sudo user; enable the firewall:
  ```bash
  sudo ufw allow OpenSSH && sudo ufw allow 'Nginx Full' && sudo ufw enable
  ```

## 2. Install packages

```bash
sudo apt update
sudo apt install -y nginx postgresql
# Go (match go.mod): install from https://go.dev/dl/ ; sqlc + golang-migrate as needed.
```

## 3. PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE ROLE site WITH LOGIN PASSWORD 'STRONG_PASSWORD';
CREATE DATABASE site OWNER site;
SQL
```
Keep Postgres bound to `127.0.0.1` (default). Put the connection string in the
backend env file.

## 4. Build & install the backend

```bash
# from the repo checkout
cd backend && make build                 # -> bin/site-backend
sudo mkdir -p /opt/site-backend /etc/site-backend
sudo cp bin/site-backend /opt/site-backend/
sudo cp deploy/systemd/site-backend.service /etc/systemd/system/

# env file (chmod 600, root-owned) — mirrors .env.example
sudo tee /etc/site-backend/site-backend.env >/dev/null <<'ENV'
APP_ENV=production
LISTEN_ADDR=127.0.0.1:8080
DATABASE_URL=postgres://site:STRONG_PASSWORD@127.0.0.1:5432/site?sslmode=disable
ADMIN_TOKEN=PASTE_openssl_rand_hex_32
ALLOW_ORIGIN=https://tomsherlock.space
ENV
sudo chmod 600 /etc/site-backend/site-backend.env

make migrate-up                          # apply schema (DATABASE_URL exported)
sudo systemctl daemon-reload
sudo systemctl enable --now site-backend
curl -fsS localhost:8080/readyz          # expect {"status":"ready"}
```

## 5. Nginx (main site)

```bash
# render placeholders, then install
sed -e 's#MAIN_DOMAIN#tomsherlock.space#g' -e 's#SITE_ROOT#/var/www/site#g' \
    backend/deploy/nginx/main-site.conf | sudo tee /etc/nginx/sites-available/main-site.conf
sudo mkdir -p /etc/nginx/snippets && sudo cp backend/deploy/nginx/proxy.conf /etc/nginx/snippets/proxy.conf
sudo ln -s /etc/nginx/sites-available/main-site.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# publish the static frontend
sudo mkdir -p /var/www/site
sudo rsync -a --exclude backend --exclude .git ./ /var/www/site/

sudo nginx -t && sudo systemctl reload nginx
```

## 6. TLS

Per-host:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tomsherlock.space -d www.tomsherlock.space
```
For many sub-apps, a single **wildcard** cert via DNS-01 avoids per-subdomain
issuance: `sudo certbot certonly --manual --preferred-challenges dns -d '*.tomsherlock.space' -d tomsherlock.space`.

## 7. Deploying updates

```bash
git pull
cd backend && make build && sudo cp bin/site-backend /opt/site-backend/ && sudo systemctl restart site-backend
# frontend only:
sudo rsync -a --exclude backend --exclude .git ./ /var/www/site/ && sudo systemctl reload nginx
```

## Operations

- Logs: `journalctl -u site-backend -f` (JSON lines from slog).
- Health: `GET /healthz` (liveness), `GET /readyz` (DB reachable).
- Sub-apps: see [subhosting.md](subhosting.md) — same systemd + Nginx pattern.
