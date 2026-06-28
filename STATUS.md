# Status Report — profile-website

**Date:** 2026-06-28
**Branch:** main (pushed to `Transcentive/profile-website`, current at `bf17f75`)
**Working tree:** clean (only `.project.md` untracked, intentionally)

## What this is

Thomas J. Sherlock's CV / portfolio site, "Digital Repertoire", a hand-authored
static HTML/CSS/JS site (no build step). Six pages: `index.html` plus five track
pages (Systems, Linguistics, Logistics, AI, Human Touch), one shared `styles.css`,
and shared chrome (nav and footer) injected from `nav.js`.

## Done this session

**Design import**
- Imported `index.html` and `track-ai.html` from the Claude Design project.
- index refresh: rebrand "Defining" to "Exploring" (hero and seal), real CV PDF
  download link, reconciled the matching `styles.css` rules (cv-strip `h3`,
  `.connect-line`, footer spacing).
- track-ai: added keyboard handlers to the Mighty Queue demo (Enter/Space on the
  focusable tier headers and cards).

**Rebrand cleanup (now consistent site-wide)**
- "scriptorium" to "repertoire", "Kinetic" to "Logistic", "Defining" to "Exploring".
- Removed the stray untracked `site/site/` duplicate directory.

**House style**
- Added `Style.md` (em-dashes are not allowed; recast per context) and referenced
  it from `CLAUDE.md`.
- Purged all 84 em-dashes across the six pages and the stylesheet, recast as
  comma / colon / parentheses / period / semicolon / middle dot. En-dash kept only
  for true ranges. Reported in `em-dash-purge-report.md` / `.html`.

**Footer**
- Consolidated six drifting inline footers into one definition in `nav.js`,
  injected on every page. Content: LinkedIn / GitHub / Substack / Sherlock
  Editorial, then the colophon "© 2026 Thomas J. Sherlock · Rutherford, NJ ·
  v.2026.05" and the seal "Architecting, Exploring, Navigating."
- Fixed a rendering bug: inject on `DOMContentLoaded` so the footer lands at the
  page bottom; cache-bust the `nav.js` include (`?v=3`) so browsers stop serving
  the stale script.

**Track-systems diagrams** (replaced two placeholders with real SVGs)
- 1.2 Enterprise Engineering & Standards: CMM maturity staircase, Level 3
  "Defined" highlighted to mark the departmental-standards work.
- 1.4 Modern Stack & Reactive Systems: six-state keg lifecycle state machine.

**Copy edits**
- Linguistics: Italian/Portuguese reframed as "specialized text-based command".
- Logistics: "Testing the waters in Texas commercial real estate".

## Current state

- All six pages serve HTTP 200 from the local server (`cd site && python3 -m http.server 8000`).
- Zero em-dashes anywhere.
- One consolidated footer, rendering at the bottom of every page.
- Everything committed and pushed.

## Open / not done

- 1.2 originally had an "Org diagram" placeholder; replaced with the CMM model
  instead (org chart added no real information for that section).
- `.project.md` remains untracked.
- No outstanding requested changes.
