#!/usr/bin/env python3
"""Generate an Nginx reverse-proxy config for a new subhosted mini-app.

Renders assets/backend-template/deploy/nginx/subhost.conf.tmpl with the given
subdomain and upstream, writing one config file per app.

Example:
  new_subhost.py --slug brewery --subdomain brewery.tomsherlock.space --upstream 127.0.0.1:9001
"""
import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "backend-template" / "deploy" / "nginx" / "subhost.conf.tmpl"


def project_root() -> Path:
    """The project to write into: the current dir's git root, else the cwd.

    Resolved from the working directory, not the skill's install location, so this
    works as a global skill in ~/.claude.
    """
    start = Path.cwd()
    for parent in [start] + list(start.parents):
        if (parent / ".git").exists():
            return parent
    return start


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="short app id, e.g. brewery")
    ap.add_argument("--subdomain", required=True, help="full subdomain, e.g. brewery.tomsherlock.space")
    ap.add_argument("--upstream", required=True, help="local upstream, e.g. 127.0.0.1:9001")
    ap.add_argument("--out", default=None, help="output file (default: <repo>/backend/deploy/nginx/<slug>.conf)")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        sys.exit(f"error: template not found at {TEMPLATE}")

    out = Path(args.out).resolve() if args.out else (project_root() / "backend" / "deploy" / "nginx" / f"{args.slug}.conf")
    out.parent.mkdir(parents=True, exist_ok=True)

    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("SUBDOMAIN", args.subdomain).replace("UPSTREAM", args.upstream)
    out.write_text(text, encoding="utf-8")

    print(f"✓ wrote {out}")
    print(f"  install:  sudo cp {out.name} /etc/nginx/sites-available/{args.slug}.conf")
    print(f"            sudo ln -s /etc/nginx/sites-available/{args.slug}.conf /etc/nginx/sites-enabled/")
    print(f"            sudo nginx -t && sudo systemctl reload nginx")
    print(f"  tls:      sudo certbot --nginx -d {args.subdomain}")


if __name__ == "__main__":
    main()
