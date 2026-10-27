# seanchaí Context Cleanup — Test Run

**Date:** 2026-10-27  
**Project:** seanchaí (Claude Project ID: `019ff039-c3a1-7613-9fff-602be4c15656`)  
**Purpose:** Second documented run of the RepoMan context cleanup workflow, validating the process before publishing a dev.to article.

The seanchaí project had been causing frequent context compaction due to a large research ledger artifact. That artifact was removed in October 2026, but 37 docs remain in the project context — a mix of handoff docs, design notes, and reference files accumulated over the project's lifetime.

---

## Inventory before cleanup

**Total docs in context:** 37 (reported pre-run)  
**Export method:** withLinda bookmarklet  
**Export file:** `seanchai-export.json`

*Filled in after export.*

---

## Step 1 — Export

**Tool:** withLinda bookmarklet  
**Action:** Ran on project page `https://claude.ai/project/019ff039-c3a1-7613-9fff-602be4c15656`  
**Output:** `seanchai-export.json`

| Metric | Value |
|--------|-------|
| Docs exported | _TBD_ |
| File size | _TBD_ |
| Export timestamp | _TBD_ |

---

## Step 2 — Summarize

**Command:**
```bash
lindakit export seanchai-export.json
```

**Results:**

| Type | Count |
|------|-------|
| handoff | _TBD_ |
| design | _TBD_ |
| changedoc | _TBD_ |
| config/ref | _TBD_ |
| other | _TBD_ |
| **Total** | _TBD_ |

**Stale handoffs flagged:** _TBD_

*Full table output appended below after run.*

---

## Step 3 — Review

**Command:**
```bash
lindakit review seanchai-export.json -o seanchai-review.json
```

**Decision breakdown:**

| Decision | Count | Notes |
|----------|-------|-------|
| keep | _TBD_ | |
| archive | _TBD_ | |
| delete | _TBD_ | |
| skip | _TBD_ | |

**Time to complete review:** _TBD_

**General observations:**
- _TBD_

---

## Step 4 — Keepers

**Command:**
```bash
lindakit keepers seanchai-review.json -o seanchai-keepers.json
```

**Output:**
- `seanchai-keepers.json` — _N_ docs

**Context reduction:** 37 → _N_ docs (_% reduction_)

---

## Step 5 — Archive

**Command:**
```bash
lindakit archive seanchai-review.json -d seanchai-archive/
```

**Archive breakdown:**

| Subfolder | Count |
|-----------|-------|
| handoffs/ | _TBD_ |
| design/ | _TBD_ |
| changedocs/ | _TBD_ |
| tests/ | _TBD_ |
| config/ | _TBD_ |
| misc/ | _TBD_ |

**Design docs to move to repo:** _TBD_

---

## Step 6 — Prune

**Tool:** Linda Prune bookmarklet  
**Action:** Ran on project page  
**Result:** All _N_ docs deleted from context

**Note:** Run only after keepers.json was confirmed ready.

---

## Step 7 — Import

**Tool:** Linda Import bookmarklet  
**File used:** `seanchai-keepers.json`  
**Result:** _N_ docs imported to project

---

## Step 8 — Repo cleanup

Design docs moved from `seanchai-archive/design/` to `seanchai/docs/` and committed.

Docs moved:
- _TBD_

---

## Outcome

| Before | After |
|--------|-------|
| 37 docs in context | _N_ docs |
| ~_N_ tokens | ~_N_ tokens |

**What was removed:**
- _TBD_ stale handoff docs
- _TBD_ design docs (moved to repo)
- _TBD_ other

**What was kept:**
- _TBD_

---

## Observations and differences from Curator run

*To be filled in after completion — comparing to the Curator cleanup run (403 files) for the dev.to article.*

---

## Comparison: seanchaí vs Curator cleanup

| | seanchaí | Curator |
|--|----------|---------|
| Starting doc count | 37 | 403 |
| Final doc count | _TBD_ | _TBD_ |
| Review time | _TBD_ | _TBD_ |
| Design docs to repo | _TBD_ | 5 |
| Surprises / issues | _TBD_ | — |
