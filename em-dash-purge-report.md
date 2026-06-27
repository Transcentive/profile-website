# Em-Dash Purge Report

**Site:** profile-website (`site/`)
**Scope:** All six pages plus the shared stylesheet
**Result:** 84 em-dashes removed, 0 remaining, all pages still serving HTTP 200

## Why

The em-dash is verboten in this site's copy. The rule now lives in `Style.md` at the
repo root and is referenced from `CLAUDE.md` so future sessions enforce it. An em-dash
is a punctuation variable: it stands in for a comma, colon, parentheses, or period
depending on context, so each instance was judged on its own rather than swapped wholesale.

## Tally by file

| File | Instances |
|------|-----------|
| index.html | 31 |
| track-ai.html | 21 |
| track-systems.html | 17 |
| track-linguistics.html | 16 |
| track-human.html | 15 |
| track-logistics.html | 10 |
| styles.css | 5 |
| **Total** | **84** |

## How each was resolved, by function

- **Colon** for lead-ins, expansions, and bold-label list items (`<b>Label</b>: text`). The majority.
- **Parentheses** for true appositive lists, e.g. `Diverse inventory (standard parcels to oversized freight)`, `three pillars (dance, music, theatre)`, `Digital Cellar (database-per-tenant isolation)`.
- **Comma** for light appositives, e.g. `The Mighty Queue, a dual-axis priority model`.
- **Period** for `State Machine Modeling.`, which avoided a double colon before the lifecycle list.
- **Semicolon** for two independent clauses in the Mighty Queue hint (`ladder; it re-sorts...`).
- **Middle dot (·)** for the `<title>` separators, the developer-facing CSS, JS, and HTML comments, and the CV-strip CSS bullet (`content: "·  "`).
- **Dropped entirely** for quote attributions (`Banquo`, `Malcolm`, `The Interdisciplinary Architect's Manifesto`), where the cite styling already sets the name off.

## Preserved

Genuine numeric ranges keep an en-dash, the one allowed dash: `§ I–V`, `2003–2006`,
`2005–2011`, `2012–2020`, `2015–2016`, `2018–2020`.

## Verification

- `grep -o "—"` across all seven files returns 0.
- All six pages return HTTP 200 from the local server.
- One subject-verb agreement slip introduced during a parenthetical recast
  (`hands control`) was caught and fixed.
