# RepoMan

**Tools and conventions for organizing repos** — how they are laid out on
every machine, the rules Claude follows in them, and the tooling that
prunes, curates and re-imports the docs in a claude.ai Project's context
window.

## Docs

| Doc | What it covers |
|---|---|
| `docs/machine-setup.md` | Where repos live on every machine (`~/projects/`) and the new-machine checklist |
| `docs/rules/` | Shared rules for Claude, used across repos (`project_rules.md`, `github_rules.md`) |
| `docs/workflow.md` | The Claude Project context cleanup workflow, with flowchart |
| `docs/naming-conventions.md` | How to name context docs so they sort themselves |
| `docs/lindakit.md` | Installing and using the `lindakit` CLI |
| `docs/roadmap.md` | What is built and what is planned |

---

## The context lifecycle tools

Over time, a Claude project accumulates hundreds of context docs. Most of
them are stale handoffs, superseded designs, or one-time notes that cost
tokens every session. RepoMan gives you a workflow to fix that.

---

## What's here

### Browser bookmarklets (`bookmarklets/`)

JavaScript bookmarklets for managing claude.ai Project docs directly from
your browser, using your existing session auth.

| Bookmarklet | What it does |
|---|---|
| **Linda Prune** | Deletes all docs from the current Project |
| **Linda Import** | Imports a keepers JSON file into the current Project |
| **Linda Refresh** | Prune + Import in one shot |

These are named in homage to [withLinda](https://github.com/withLinda/claude-project-knowledge-exporter),
whose export bookmarklet is the prerequisite for this workflow. The name also
happens to mean "pretty" in Spanish — which is what the context window
looks like after a cleanup.

**See** `bookmarklets/README.md` for setup and usage.

### Python CLI (`lindakit/`)

`lindakit` is a local analysis tool for the export JSON that withLinda produces.
No browser auth required — it works entirely with local files.

```
lindakit export        # pretty-print / summarize the exported JSON
lindakit review        # interactive review: mark each doc keep/archive/delete
lindakit archive       # organize archive files into subfolders by type
lindakit keepers       # generate keepers.json from your review decisions
```

**See** `docs/lindakit.md` for installation and usage.

---

## Workflow overview

1. **Export** current Project docs with the [withLinda bookmarklet](https://github.com/withLinda/claude-project-knowledge-exporter)
2. **Summarize** with `lindakit export` (will also write `review.json` with default decisions)
3. **Review** (optional) with `lindakit review` to edit those defaults
4. **Archive everything** with `lindakit archive`, sorted into typed folders
5. **Write** `keepers.json` with `lindakit keepers`
6. **Commit and push** the export, archive and keepers, and confirm they are on GitHub
7. **Prune** the Project with the Linda Prune bookmarklet
8. **Import** your keepers with the Linda Import bookmarklet

Nothing is lost: everything is archived and committed before anything is deleted.

Full walkthrough and a flowchart: `docs/workflow.md`
How to name docs so they sort themselves: `docs/naming-conventions.md`
What is built and what is planned: `docs/roadmap.md`

---

## License

AGPL-3.0-or-later. See `LICENSE`.

The AGPL was chosen deliberately: this tool should stay free for everyone.
If you wrap it in a service and charge for access, the AGPL requires you
to publish that service's source code too.

## Copyright

Copyright (C) 2026 Carolyn Boyle

## Attribution

The withLinda bookmarklet (`bookmarklets/README.md` has the link) is a
prerequisite for this workflow. RepoMan does not copy or bundle withLinda's
code — it references and builds on the workflow she established.
