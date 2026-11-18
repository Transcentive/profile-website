#!/usr/bin/env python3
"""Scaffold a Go backend for a website from the bundled template.

Copies assets/backend-template/ into a target directory (default: <repo>/backend),
renames *.tmpl files (e.g. go.mod.tmpl -> go.mod), substitutes placeholders, and
optionally runs `sqlc generate`, `go mod tidy`, and `go build ./...`.

Examples:
  scaffold_backend.py                                  # default module: tomsherlock.space/backend
  scaffold_backend.py --module example.com/backend     # override the module path
  scaffold_backend.py --target /tmp/backend-test --no-build
  scaffold_backend.py --domain tomsherlock.space --site-root /var/www/site
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "backend-template"
DEFAULT_MODULE = "tomsherlock.space/backend"

# Files we never try to read as text for substitution.
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".woff", ".woff2", ".ico"}


def project_root() -> Path:
    """The project to scaffold into: the current dir's git root, else the cwd.

    Resolved from the working directory (where the skill is invoked), NOT from the
    skill's own install location — so this works as a global skill in ~/.claude.
    """
    start = Path.cwd()
    for parent in [start] + list(start.parents):
        if (parent / ".git").exists():
            return parent
    return start


def substitute(text: str, repl: dict) -> str:
    for key, val in repl.items():
        if val is not None:
            text = text.replace(key, val)
    return text


def copy_template(target: Path, repl: dict, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            sys.exit(f"error: target {target} exists and is not empty (use --force)")
    target.mkdir(parents=True, exist_ok=True)

    for src in sorted(TEMPLATE_DIR.rglob("*")):
        rel = src.relative_to(TEMPLATE_DIR)
        dst = target / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        # Strip a single trailing .tmpl on the destination filename.
        if dst.name.endswith(".tmpl"):
            dst = dst.with_name(dst.name[: -len(".tmpl")])
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in BINARY_SUFFIXES:
            shutil.copy2(src, dst)
            continue
        text = src.read_text(encoding="utf-8")
        dst.write_text(substitute(text, repl), encoding="utf-8")
    print(f"✓ template copied to {target}")


def run(cmd: list, cwd: Path) -> bool:
    print(f"  $ {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
        return True
    except FileNotFoundError:
        print(f"  ! {cmd[0]} not found — skipping")
    except subprocess.CalledProcessError as e:
        print(f"  ! {cmd[0]} failed (exit {e.returncode})")
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", default=DEFAULT_MODULE, help="Go module path")
    ap.add_argument("--target", default=None, help="output dir (default: <repo>/backend)")
    ap.add_argument("--domain", default=None, help="main domain (substitutes MAIN_DOMAIN)")
    ap.add_argument("--site-root", default=None, help="static site root (substitutes SITE_ROOT)")
    ap.add_argument("--no-build", action="store_true", help="skip sqlc/go steps")
    ap.add_argument("--force", action="store_true", help="overwrite non-empty target")
    args = ap.parse_args()

    target = Path(args.target).resolve() if args.target else (project_root() / "backend")
    repl = {
        "MODULE_PATH": args.module,
        "MAIN_DOMAIN": args.domain,
        "SITE_ROOT": args.site_root,
    }

    copy_template(target, repl, args.force)

    if args.no_build:
        print("\nNext steps:\n  cd %s && sqlc generate && go mod tidy && go build ./..." % target)
        return

    print("\nGenerating code and building:")
    if run(["sqlc", "generate"], target):
        run(["go", "mod", "tidy"], target)
        run(["go", "build", "./..."], target)
    else:
        print("  install sqlc (https://sqlc.dev) then re-run, or use --no-build")


if __name__ == "__main__":
    main()
