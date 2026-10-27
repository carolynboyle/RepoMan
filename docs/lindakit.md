# lindakit — Python CLI Reference

`lindakit` is the local analysis and file-management half of RepoMan.
It works entirely with local files — no browser, no claude.ai auth required.

---

## Installation

```bash
cd lindakit/
pip install -e .
```

Or, if your project uses a virtualenv:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e lindakit/
```

---

## Commands

### `lindakit export [EXPORT_JSON]`

Summarize an export file from withLinda.

```bash
lindakit export docs/context/exports/2026-10-27.json
```

Prints a table showing each doc's filename, auto-detected type, word count,
and any flags (e.g. "stale" for handoffs from before the current month).

**Auto-detected types:**
| Type | Pattern |
|---|---|
| handoff | filename contains `handoff` + a date |
| design | filename starts with `DESIGN_` or ends with `_design` |
| changedoc | filename contains `changedoc`, `change_doc`, or `changeset` |
| test | filename starts with `test_` or ends with `_test` |
| config/ref | filename contains `config`, `settings`, `rules`, or `conventions` |
| other | everything else |

---

### `lindakit review [EXPORT_JSON] [-o REVIEW_JSON]`

Interactively review each doc. Default output: `review.json`.

```bash
lindakit review docs/context/exports/2026-10-27.json -o docs/context/review.json
```

For each doc, shows:
- Filename and auto-detected type
- Word count
- First 300 characters of content

Then prompts for a decision:
- `k` — **keep** (included in keepers.json)
- `a` — **archive** (organized by `lindakit archive`)
- `d` — **delete** (excluded from everything)
- `s` — **skip** (decide later; will be prompted again on resume)
- `q` — **quit** (saves progress; resume by running again)

Already-decided docs (non-skip) are skipped on resume, so you can work
through a large export in multiple sessions.

---

### `lindakit keepers [REVIEW_JSON] [-o KEEPERS_JSON]`

Generate `keepers.json` for Linda Import. Default output: `keepers.json`.

```bash
lindakit keepers docs/context/review.json -o docs/context/keepers.json
```

Reads the review file and writes a JSON array of every doc marked `keep`:

```json
[
  { "file_name": "project_rules.md", "content": "..." },
  { "file_name": "sql_conventions.md", "content": "..." }
]
```

This is the file Linda Import reads. Give it to the bookmarklet and the
Project gets exactly these docs.

---

### `lindakit archive [REVIEW_JSON] [-d OUTPUT_DIR]`

Organize archived docs into typed subfolders. Default output: `./archive`.

```bash
lindakit archive docs/context/review.json -d docs/context/archive/
```

Writes each doc marked `archive` as a `.md` file into a typed subfolder:

```
docs/context/archive/
  handoffs/
  design/
  changedocs/
  tests/
  config/
  misc/
```

From here you can move design docs into your repo's `docs/roadmap/`
and commit them to version control.

---

## Review file format

The review JSON is a plain array of doc entries with an added `decision` field:

```json
[
  {
    "file_name": "project_rules.md",
    "content": "# Project Rules\n\n...",
    "uuid": "optional-uuid-from-export",
    "decision": "keep"
  },
  {
    "file_name": "curator_handoff_2026-07-04.md",
    "content": "...",
    "uuid": "...",
    "decision": "archive"
  }
]
```

You can edit this file by hand if you prefer. `lindakit review` reads
existing decisions and resumes from where the first `skip` or un-decided
entry appears.
