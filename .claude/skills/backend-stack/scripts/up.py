#!/usr/bin/env python3
"""Orchestrator: scaffold a Go backend (the site-backend skill) and provision its
local database (the provision-db skill) in one chained run.

The directory produced by step 1 is passed straight into step 2 as --backend-dir
— so the migrations applied and the .env written in step 2 target exactly what
step 1 just created. No manual handoff.

End state: a compiling backend/ with a local PostgreSQL database, migrated, and a
ready-to-run .env.
"""
import argparse
import subprocess
import sys
from pathlib import Path

# The three skills sit side by side in the repository's .claude/skills/.
SKILLS = Path(__file__).resolve().parents[2]
SCAFFOLD = SKILLS / "site-backend" / "scripts" / "scaffold_backend.py"
PROVISION = SKILLS / "provision-db" / "scripts" / "setup_local_db.py"


def run(cmd) -> None:
    print("  $ " + " ".join(str(c) for c in cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit("\n✗ step failed (exit %d) — stopping the chain." % res.returncode)


def main():
    ap = argparse.ArgumentParser(description="Scaffold a backend AND provision its local DB in one run.")
    ap.add_argument("--module", default="tomsherlock.space/backend", help="Go module path (step 1)")
    ap.add_argument("--domain", default=None, help="site domain — fills Nginx config and CORS origin")
    ap.add_argument("--site-root", default=None, help="static-site root on the server (step 1 Nginx config)")
    ap.add_argument("--target", default="backend", help="backend output dir (default: backend)")
    ap.add_argument("--db-name", default="site")
    ap.add_argument("--db-user", default="site")
    ap.add_argument("--allow-origin", default=None, help="CORS origin for .env (default: https://<domain>)")
    ap.add_argument("--force", action="store_true", help="overwrite existing backend/ and .env")
    args = ap.parse_args()

    for p in (SCAFFOLD, PROVISION):
        if not p.exists():
            sys.exit("required skill script missing: %s" % p)

    print("══ 1/2  Scaffold backend (site-backend) ══")
    scaffold = [sys.executable, str(SCAFFOLD), "--module", args.module, "--target", args.target]
    if args.domain:
        scaffold += ["--domain", args.domain]
    if args.site_root:
        scaffold += ["--site-root", args.site_root]
    if args.force:
        scaffold += ["--force"]
    run(scaffold)

    print("\n══ 2/2  Provision local database (provision-db) ══")
    provision = [sys.executable, str(PROVISION), "--backend-dir", args.target,
                 "--db-name", args.db_name, "--db-user", args.db_user]
    origin = args.allow_origin or ("https://%s" % args.domain if args.domain else None)
    if origin:
        provision += ["--allow-origin", origin]
    if args.force:
        provision += ["--force"]
    run(provision)

    print("\n✓ Stack ready.")
    print("  Start it:  cd %s && set -a && source .env && set +a && make run" % args.target)
    print("  Verify:    curl localhost:8080/healthz  &&  curl localhost:8080/readyz")


if __name__ == "__main__":
    main()
