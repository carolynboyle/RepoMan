# seanchai Context Cleanup: Run Record

**Project:** seanchai (Claude Project ID `019ff039-c3a1-7613-9fff-602be4c15656`)
**Export taken:** 2026-10-27
**Status:** archive and keepers committed (2026-11-06); **prune and import pending**
**Purpose:** second documented run of the cleanup workflow, validating the
process before publishing a dev.to article.

The seanchai project was hitting frequent context compaction because of a
large research ledger artifact. The artifact was removed in October 2026, but
37 docs remained in the context: handoffs, design notes and reference files
accumulated over the project's life.

Source of the figures below: `docs/context/exports/seancha.json`,
`review.json` and `keepers.json` in the seanchai repo. Token counts are the
estimates reported in the export.

---

## Inventory before cleanup

| Metric | Value |
|---|---|
| Docs in context | 37 |
| Unique docs (after merging duplicates) | 30 |
| Estimated tokens | 103,894 |
| Tokens in duplicate copies | 18,749 |
| Doc dates (`created_at`) | 2026-09-08 to 2026-10-21 |
| Export file | `exports/seancha.json`, 405,929 bytes |

Seven of the 37 docs were exact duplicates of another doc: four were the same
doc stored under a `claude/` name prefix as well as a bare name, and three had
the same name stored twice.

## Step 1: Export

withLinda bookmarklet on the project page; saved as `exports/seancha.json`.
Committed to the seanchai repo so the uuids are kept.

## Step 2: Summarize

Docs sorted by the rules in `docs/context/lindakit.yaml` (30 unique docs):

| Type | Docs | Default |
|---|---|---|
| handoffs | 10 | archive |
| reference | 6 | keep |
| research | 5 | keep |
| memoir | 3 | 2 keep, 1 archive |
| search_results | 2 | archive |
| substack | 2 | archive |
| design | 1 | archive |
| prompts | 1 | archive |

Run on paper against the real export, the yaml's defaults reproduced the
hand-made decisions exactly (13 keep, 17 archive, 0 mismatches).

## Step 3: Review

Decisions in `review.json` (37 entries, one per copy):

| Decision | Count | Notes |
|---|---|---|
| keep | 13 | reference and research docs, plus two memoir notes |
| archive | 17 | handoffs, search results, substack summaries, design, prompts |
| delete | 7 | all seven are the duplicate copies; the other copy of each was kept or archived, so no content was lost |
| skip | 0 | |

Review time: not recorded.

## Step 4: Keepers

`keepers.json`: 13 docs, about 35,002 estimated tokens.

| | Before | After keepers | Change |
|---|---|---|---|
| Docs | 37 | 13 | -65% |
| Estimated tokens | 103,894 | 35,002 | -66% |

## Step 5: Archive

17 docs written to `docs/context/archive/` (committed `b7ee104`):

| Subfolder | Docs |
|---|---|
| handoffs/ | 10 |
| design/ | 1 |
| misc/ | 6 |

This first archive held only the docs marked archive, and `misc/` was a
catch-all. The workflow was then revised to archive every doc into typed
folders; see `docs/workflow.md` and `docs/naming-conventions.md`.

## Step 6: Commit and push

Raw export committed (`b5066f0`), archive committed (`b7ee104`),
`lindakit.yaml` committed (`3a7e7a6`). Confirmed on GitHub.

## Step 7: Prune

**Pending.**

## Step 8: Import

**Pending.** Input will be `docs/context/keepers.json` (13 docs).

## Step 9: Wrap up

**Pending.** Design doc to copy to `docs/roadmap/` (route `design`), search
results to `docs/search/`, memoir notes to `docs/memoir/`.

---

## Observations

- **Duplicates are common.** A fifth of the docs (7 of 37) were copies. A
  `claude/` prefix on a name makes the same doc look different to a tool that
  matches on file name. Merging duplicates by normalized name and content
  hash is part of the planned design.
- **Name-based type detection misses real docs.** `conversation-summary-*`
  and `session-summary-*` are handoffs, but the original patterns only matched
  names containing "handoff" and a date. This is what a per-repo
  `lindakit.yaml` fixes, and a `<type>__<name>` prefix avoids entirely.
- **Delete is the wrong word.** Every "delete" here was a duplicate. Once
  everything is archived first, the only decision left is keep or archive-only.
- **Review is not the safety net.** Committing the raw export is. Review only
  decides what returns to the Project.

## Comparison: seanchai vs Curator cleanup

| | seanchai | Curator |
|--|----------|---------|
| Starting doc count | 37 | 403 |
| Unique docs | 30 | not recorded |
| Final doc count | 13 (planned; import pending) | not recorded |
| Review time | not recorded | not recorded |
| Design docs to repo | 1 | 5 |
| Surprises / issues | 7 duplicate copies; names with `claude/` prefix | not recorded |
