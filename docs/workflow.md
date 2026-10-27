# RepoMan Workflow

A complete walkthrough of the context cleanup process, from bloated Project
to clean, curated context window.

---

## The problem

Claude Projects accumulate docs over time. Every handoff, design note,
and scratch file from months of work sits in the context window, consuming
tokens in every session. Most of it is obsolete.

The solution is periodic context review: export everything, decide what
stays, prune the Project, and re-import only the keepers.

---

## Prerequisites

1. **withLinda's exporter bookmarklet** — the starting point for this
   whole workflow. Install it from:
   https://github.com/withLinda/claude-project-knowledge-exporter

2. **lindakit** (optional, for the review step) — install with:
   ```
   pip install -e lindakit/
   ```
   Or use any other method to decide which docs to keep.

3. **Linda bookmarklets** — install from `bookmarklets/`. See
   `bookmarklets/README.md` for setup.

---

## Filesystem convention

All context lifecycle files live under `docs/context/` in the project repo:

```
docs/context/
  exports/                    ← withLinda raw exports, one per cleanup run
    2026-10-27.json
  review.json                 ← lindakit review output
  keepers.json                ← commit this — record of what's in context
  archive/                    ← lindakit archive output
    handoffs/
    design/
    changedocs/
    tests/
    config/
    misc/
```

Add this to your repo's `.gitignore` to exclude ephemeral working files:

```
# context lifecycle working files
docs/context/exports/
docs/context/review.json
```

`keepers.json` is worth committing — it's a record of what was in context
at the time of the last cleanup.

---

## Step 1 — Export

Navigate to your Claude Project page and run the **withLinda** bookmarklet.
Save the downloaded JSON as `docs/context/exports/YYYY-MM-DD.json`.

---

## Step 2 — Summarize (optional)

```bash
lindakit export docs/context/exports/2026-10-27.json
```

Prints a table of all docs with their auto-detected type (handoff, design,
config/ref, etc.) and flags stale handoffs. Gives you a quick picture of
what's in the Project before you start deciding.

---

## Step 3 — Review

```bash
lindakit review docs/context/exports/2026-10-27.json -o docs/context/review.json
```

Interactive prompt for each doc:

```
╭─ 1/47 ───────────────────────────────────────────────╮
│ seanchai_register_handoff_2026-10-22.md               │
│ handoff · 1,240 words                                 │
│                                                       │
│ # Seanchai Register — Handoff 2026-10-22 ...          │
╰───────────────────────────────────────────────────────╯

Decision (k/a/d/s/q): k
→ keep
```

Decisions are saved to `docs/context/review.json` after each entry. You
can quit and resume — already-decided docs are skipped on resume.

**Decision keys:**
- `k` — keep (will go into keepers.json for re-import)
- `a` — archive (will be written to organized subfolders by `lindakit archive`)
- `d` — delete (excluded from everything)
- `s` — skip (decide later; re-reviewing will prompt again)
- `q` — quit and save progress

**General heuristics:**
- **Keep** — evergreen references (project rules, SQL conventions, active
  handoffs from the current month)
- **Archive** — design docs (→ repo `docs/` or `roadmap/`), stale handoffs
  (pre-current-month), completed changedocs
- **Delete** — true scratch files, duplicates, empty or near-empty docs

---

## Step 4 — Generate keepers.json

```bash
lindakit keepers docs/context/review.json -o docs/context/keepers.json
```

Writes `docs/context/keepers.json` — a JSON array of `{ file_name, content }`
objects for every doc marked `keep`. This is the file Linda Import reads.

---

## Step 5 — Organize archive files (optional)

```bash
lindakit archive docs/context/review.json -d docs/context/archive/
```

Writes archived docs as `.md` files into typed subfolders:

```
docs/context/archive/
  handoffs/        ← stale handoff docs
  design/          ← DESIGN_* and *_design docs
  changedocs/      ← changedoc_*, change_doc_*, etc.
  tests/           ← test_* docs
  config/          ← config, rules, conventions docs
  misc/            ← everything else
```

From here you can move design docs into your repo's `docs/roadmap/`,
commit them to git, and remove them from the Project.

---

## Step 6 — Prune the Project

Navigate to your Claude Project page and click **Linda Prune**.

This deletes all current docs from the Project. There is no undo —
run it only after you have `docs/context/keepers.json` ready.

---

## Step 7 — Import keepers

Click **Linda Import** on the Project page, then select
`docs/context/keepers.json`.

The bookmarklet will POST each keeper doc to the Project API and show
progress. When it's done, your Project has exactly the docs you chose.

---

## Step 8 — Clean the repo

For design docs you archived: move them from `docs/context/archive/design/`
to your repo's `docs/roadmap/` (or wherever they belong) and commit.
Commit `docs/context/keepers.json` as a record of the cleanup.

The repo is the right home for design docs — they're version-controlled,
linkable, and fetchable in future Claude sessions. The Project context
window is for active references only.

---

## Shortcuts

**Linda Refresh** combines Prune + Import in one bookmarklet. Use it when
you've already done the review and just want to reset the context:

1. Generate `docs/context/keepers.json`
2. Click Linda Refresh
3. Select `docs/context/keepers.json`
4. Done

---

## Suggested cadence

- **Monthly** — review and trim. Anything older than a month that isn't an
  evergreen reference probably doesn't need to be in context.
- **After a major feature** — once a changedoc is shipped, it goes to
  archive, not context.
- **When context feels bloated** — `lindakit export` will show you the
  token footprint immediately.
