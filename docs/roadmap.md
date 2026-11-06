# RepoMan Roadmap

Features and integrations planned but not yet built.

---

## lindakit and the context workflow

The workflow in `docs/workflow.md` is the target. This section tracks what
is still needed to get there.

### Planned

- [ ] `lindakit export` writes `review.json` with default decisions from the
      type rules, so review is optional
- [ ] `lindakit archive` writes every doc, merges duplicates, and flattens
      `/` in names
- [ ] Load `docs/context/lindakit.yaml` with the three-layer resolution
      (built-in defaults, repo yaml, human decisions)
- [ ] Sort by `<type>__<name>` prefix with no yaml entry
- [ ] `lindakit rename`: dry run by default, apply with `git mv`, write an
      old-name to new-name map
- [ ] Routes: copy archived docs of a type to a repo destination
- [ ] Restore: build a `keepers.json`-shaped list from chosen archive files
- [ ] Tests and a clean Pylint run (required by `project_rules.md`)

### Known bugs (found 2026-11-06 reading the 2026-10-27 scaffold)

- `lindakit/pyproject.toml`: `build-backend = "setuptools.backends.legacy:build"`
  is not a real backend (the module does not exist), so
  `pip install -e lindakit/` should fail. It should be
  `setuptools.build_meta`.
- `archive.py` writes `dest_dir / name` without flattening, so a name such as
  `claude/foo.md` creates a nested folder.
- `review.py` finds existing decisions by `file_name`, so two docs with the
  same name collide: the second is treated as already decided.
- `cli.py`: the `archive` argument is named `EXPORT_JSON`, but the organizer
  reads decisions from a review file. The docs pass `review.json`, which is
  what works.
- No `tests/` directory.

---

## Curator integration — Repo Man role

The bookmarklets and `lindakit` CLI are standalone tools that work outside
Curator. The longer-term goal is a **Repo Man role** inside Curator that
surfaces the same workflow from the UI, with project context data stored
in Postgres.

### Command snippets library

**Goal:** A `commands` table in the Curator database that stores commonly-used
shell and git commands, associated with roles. The Repo Man role surfaces
GitHub commands as copy-to-clipboard buttons — "Set GitHub credentials,"
"Clone repo," "Set remote URL to SSH," etc. — so you don't have to look
up syntax you use infrequently.

**Why Curator / why Postgres:** The commands belong with the project
management data. The Repo Man role is the natural context — you're in a
coding project, you need a GitHub command, the button is right there.

**Schema sketch (not yet designed):**
- `commands` table: `id`, `name`, `command_text`, `role`, `description`,
  `created_at`, `updated_at`
- Role association determines which commands surface in which Curator role
- UI: a `copy_button` field type in fieldkit, or a role-specific template
  section — TBD when this is scoped

**Reference:** https://github.com/carolynboyle/RepoMan (this repo) — the
standalone tools here inform what the Curator implementation needs to support.

---

## GitHub commands for context lifecycle

The Repo Man role should also surface the commands specific to the
context cleanup workflow:

- Clone a repo into the session
- Push after scaffolding
- Switch remote to SSH
- Check auth status

These are the commands that currently require looking up syntax. The pattern
from the bookmarklets (auto-detect project from URL, act on it) should
inform how the Curator role surfaces the equivalent git operations
(auto-detect repo from the active project record).

---

## Curator Repo Man crew role

Full integration of the RepoMan workflow as a Curator crew member role:

- Links to context export/import bookmarklets from the project view
- Stores keepers decisions in Postgres (reviewable, auditable)
- Surfaces archive file locations (repo path where the doc was moved)
- Command snippets library (above)

This is the end state; the standalone bookmarklets and `lindakit` are the
path to understanding what the Curator implementation needs to do.
