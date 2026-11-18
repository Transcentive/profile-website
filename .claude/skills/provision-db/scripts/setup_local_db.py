#!/usr/bin/env python3
"""Provision a local PostgreSQL database + user for a site-backend, apply its
schema migrations, and write a ready-to-run .env. Idempotent and safe to re-run.

Three steps:
  1. Create the LOGIN role and the database if they don't already exist.
  2. Apply every db/migrations/*.up.sql into the database (skipped if the schema
     is already present, unless --force-migrate).
  3. Write <backend-dir>/.env with the resulting DATABASE_URL + a generated
     ADMIN_TOKEN (an existing .env is left untouched unless --force).

Assumes a local PostgreSQL you can administer as a superuser over the default
connection (Homebrew/macOS: your own OS user). Override the admin connection
with --superuser / --maintenance-db if your setup differs.
"""
import argparse
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, quote


def fail(msg: str) -> None:
    print("  ✗ " + msg, file=sys.stderr)
    sys.exit(1)


def psql_super(args, sql: str, capture: bool = True) -> str:
    """Run SQL against the maintenance DB as an administrator."""
    cmd = ["psql", "-v", "ON_ERROR_STOP=1", "-d", args.maintenance_db]
    if args.superuser:
        cmd += ["-U", args.superuser]
    cmd += ["-tAc", sql] if capture else ["-c", sql]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        fail("psql (admin) failed: " + res.stderr.strip())
    return res.stdout.strip()


def psql_dsn(dsn: str, sql: str = None, file: Path = None):
    """Run SQL or a file against the target DB as the app user (via the DSN)."""
    cmd = ["psql", dsn, "-v", "ON_ERROR_STOP=1"]
    cmd += ["-f", str(file)] if file else ["-tAc", sql]
    return subprocess.run(cmd, capture_output=True, text=True)


def parse_env(path: Path) -> dict:
    vals = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
    return vals


def build_env(example: Path, dsn: str, admin_token: str, allow_origin: str) -> str:
    if example.exists():
        out = []
        for line in example.read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                out.append("DATABASE_URL=" + dsn)
            elif line.startswith("ADMIN_TOKEN="):
                out.append("ADMIN_TOKEN=" + admin_token)
            elif line.startswith("ALLOW_ORIGIN=") and allow_origin:
                out.append("ALLOW_ORIGIN=" + allow_origin)
            else:
                out.append(line)
        return "\n".join(out) + "\n"
    return (
        "APP_ENV=development\n"
        "LISTEN_ADDR=127.0.0.1:8080\n"
        "DATABASE_URL=" + dsn + "\n"
        "ADMIN_TOKEN=" + admin_token + "\n"
        "ALLOW_ORIGIN=" + (allow_origin or "*") + "\n"
    )


def main():
    ap = argparse.ArgumentParser(description="Provision a local Postgres DB+user, migrate, write .env.")
    ap.add_argument("--backend-dir", default="backend", help="backend dir holding db/migrations and receiving .env")
    ap.add_argument("--db-name", default="site")
    ap.add_argument("--db-user", default="site")
    ap.add_argument("--db-password", default=None, help="default: reuse existing .env, else generate")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", default="5432")
    ap.add_argument("--admin-token", default=None, help="default: reuse existing .env, else generate")
    ap.add_argument("--allow-origin", default=None, help="CORS origin written into .env (e.g. https://tomsherlock.space)")
    ap.add_argument("--migrations", default=None, help="default: <backend-dir>/db/migrations")
    ap.add_argument("--superuser", default=None, help="admin role to connect as (default: current OS user)")
    ap.add_argument("--maintenance-db", default="postgres")
    ap.add_argument("--force", action="store_true", help="overwrite an existing .env")
    ap.add_argument("--force-migrate", action="store_true", help="apply migrations even if tables already exist")
    args = ap.parse_args()

    backend = Path(args.backend_dir).resolve()
    if not backend.exists():
        fail("backend dir not found: %s" % backend)
    migrations = Path(args.migrations).resolve() if args.migrations else backend / "db" / "migrations"
    env_path = backend / ".env"
    example = backend / ".env.example"
    existing = parse_env(env_path)

    # Reuse secrets from an existing .env so repeated runs stay consistent.
    password = args.db_password
    if not password and existing.get("DATABASE_URL"):
        try:
            password = urlparse(existing["DATABASE_URL"]).password
        except Exception:
            password = None
    if not password:
        password = secrets.token_hex(16)

    admin_token = args.admin_token
    if not admin_token:
        prev = existing.get("ADMIN_TOKEN", "")
        admin_token = prev if prev and "CHANGE_ME" not in prev else secrets.token_hex(32)

    dsn = "postgres://%s:%s@%s:%s/%s?sslmode=disable" % (
        args.db_user, quote(password, safe=""), args.host, args.port, args.db_name)

    # --- Step 1: role + database -------------------------------------------
    print("Step 1/3 — role + database")
    pw_sql = password.replace("'", "''")
    if psql_super(args, "SELECT 1 FROM pg_roles WHERE rolname = '%s'" % args.db_user) == "1":
        psql_super(args, "ALTER ROLE \"%s\" WITH LOGIN PASSWORD '%s'" % (args.db_user, pw_sql), capture=False)
        print("  • role '%s' exists — password synced" % args.db_user)
    else:
        psql_super(args, "CREATE ROLE \"%s\" WITH LOGIN PASSWORD '%s'" % (args.db_user, pw_sql), capture=False)
        print("  ✓ created role '%s'" % args.db_user)

    if psql_super(args, "SELECT 1 FROM pg_database WHERE datname = '%s'" % args.db_name) == "1":
        print("  • database '%s' exists" % args.db_name)
    else:
        psql_super(args, "CREATE DATABASE \"%s\" OWNER \"%s\"" % (args.db_name, args.db_user), capture=False)
        print("  ✓ created database '%s' (owner %s)" % (args.db_name, args.db_user))

    # --- Step 2: migrations -------------------------------------------------
    print("Step 2/3 — schema migrations")
    if not migrations.exists():
        fail("migrations dir not found: %s" % migrations)
    files = sorted(migrations.glob("*.up.sql"))
    if not files:
        fail("no *.up.sql files in %s" % migrations)

    probe = psql_dsn(dsn, sql="SELECT count(*) FROM information_schema.tables "
                              "WHERE table_schema='public' AND table_type='BASE TABLE'")
    if probe.returncode != 0:
        fail("cannot connect to '%s' as '%s': %s" % (args.db_name, args.db_user, probe.stderr.strip()))
    if probe.stdout.strip() not in ("0", "") and not args.force_migrate:
        print("  • %s table(s) already present — skipping (use --force-migrate to re-apply)" % probe.stdout.strip())
    else:
        for f in files:
            res = psql_dsn(dsn, file=f)
            if res.returncode != 0:
                fail("migration %s failed: %s" % (f.name, res.stderr.strip()))
            print("  ✓ applied %s" % f.name)

    # --- Step 3: .env -------------------------------------------------------
    print("Step 3/3 — .env")
    if env_path.exists() and not args.force:
        print("  • %s exists — left untouched (use --force to regenerate)" % env_path)
    else:
        env_path.write_text(build_env(example, dsn, admin_token, args.allow_origin), encoding="utf-8")
        print("  ✓ wrote %s" % env_path)

    print("\nDone. Local database ready.")
    print("  DATABASE_URL = %s" % dsn)
    print("  run: cd %s && set -a && source .env && set +a && make run" % backend)


if __name__ == "__main__":
    main()
