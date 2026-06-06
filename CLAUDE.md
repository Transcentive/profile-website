# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal CV / portfolio website for Thomas J. Sherlock, themed as a "Digital Scriptorium" — a parchment-and-ink editorial aesthetic blending ancient Sumerian/cuneiform motifs with a modern software résumé. It is **hand-authored static HTML/CSS/JS**: no build step, no framework, no package manager, no tests, no transpilation. Files are served as-is.

All site files live under `site/`.

## Running / previewing

There is nothing to build. Open `site/index.html` directly, or serve the folder over HTTP (needed so `nav.js` and relative asset paths resolve cleanly):

```sh
cd site && python3 -m http.server 8000   # then visit http://localhost:8000
```

This is not a git repository.

## Structure

- `site/index.html` — landing page: hero, the five "tracks" overview, CV strip, footer. Also hosts the **edit-mode/Tweaks** widget (see below).
- `site/track-systems.html`, `track-linguistics.html`, `track-logistics.html`, `track-ai.html`, `track-human.html` — one deep-dive page per track (Tracks 01–05).
- `site/styles.css` — single shared stylesheet for every page.
- `site/nav.js` — single shared nav, injected at runtime.
- `site/assets/` — hand-sketch PNGs, referenced with a `?v=N` cache-busting query string (bump `N` when replacing an image).

## Conventions to preserve when editing

**Every page** wires up the same boilerplate — replicate it exactly when adding a page:
- The same Google Fonts `<link>` block (Cormorant Garamond, Inter, JetBrains Mono, Playfair Display; index also loads Noto Sans Cuneiform) and `<link rel="stylesheet" href="styles.css">`.
- A nav mount + script: `<div id="site-nav"></div>` immediately followed by `<script src="nav.js"></script>`.
- An inline `IntersectionObserver` at the end of `<body>` that adds the `in` class to every `.reveal` element as it scrolls into view. Animated sections must carry `class="reveal"`.
- A `<footer class="footer" id="connect">` and `data-screen-label="..."` attributes on major sections (these label screens for design/review tooling — keep them numbered and descriptive).

**Navigation is centralized.** Do not hardcode nav links in pages. Edit the `NAV_ITEMS` array in `nav.js`; it renders the bar and auto-marks the current page `active` by matching `location.pathname`. Adding a track page = adding one entry there.

**Styling is token-driven.** Colors come from CSS custom properties in `:root` at the top of `styles.css` (`--parchment`, `--ink`, `--oxblood`, `--gold`, `--silver`, etc.). Use these variables rather than raw hex. The three signature accent words map to a recurring color triad: silver = "Architecting", gold = "Defining", oxblood/`ox` = "Navigating".

**Track pages** follow a fixed template: `.page-hero` with breadcrumbs and an `.uppertrack` tag, a `.page-body` with a sticky `.toc` of module anchors (`#m1`…`#mN`) beside an `.content` article of numbered `<section>` modules, then a `.page-pager` (prev/next), then the shared footer.

**The footer is duplicated inline on every page** (unlike the nav, it is not centralized). The `<footer class="footer" id="connect">` block — including the Email / phone / LinkedIn / GitHub / Substack contact links — is copy-pasted into all six pages. Any change to footer content (e.g. updating a social URL) must be applied to `index.html` and all five `track-*.html` files; a `sed` replace across `site/*.html` is the practical way to keep them in sync.

## Edit-mode / "Tweaks" protocol (index.html only)

`index.html` contains a self-contained word-swap widget driven by `postMessage` from a parent frame (a design/editing host). Key pieces:
- The live config is the object literal between the `/*EDITMODE-BEGIN*/` and `/*EDITMODE-END*/` markers — an external editor rewrites this region, so keep those exact comment sentinels intact.
- Swappable words are tagged in markup with `class="tw-word"` (swaps "scriptorium") and `class="tw-kin"` (swaps the "kinetic(s)" stem). Original text is snapshotted on load so swaps stay reversible.
- It listens for `__activate_edit_mode` / `__deactivate_edit_mode` and posts `__edit_mode_available`, `__edit_mode_set_keys`, and `__edit_mode_dismissed` back to `window.parent`. Don't rename these message types or class hooks unless updating both sides.

This widget exists only on `index.html`; other pages don't include it.
