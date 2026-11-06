# Context File Naming Conventions

How to name docs in a Claude Project so the context lifecycle tools
(`lindakit`) can sort them with no configuration, in any repo.

> **Status:** the convention itself works today as a naming habit. Prefix
> routing in `lindakit` and the `lindakit rename` command are designed but
> not yet implemented; this document is the spec they will follow.

---

## The rule

```
<type>__<name>.md
```

- `<type>` is the folder the doc belongs in: lowercase letters, digits and
  single underscores (`handoffs`, `search_results`, `reference`).
- `__` (two underscores) separates type from name. It is the only place a
  double underscore may appear.
- `<name>` is lowercase, hyphen-separated, no spaces. Use ISO dates
  (`2026-11-06`) when a date matters, and put them at the end.
- No slashes. The Projects tool namespaces docs written by Claude under
  `claude/`; `lindakit` strips that prefix, so never type it yourself.

Examples:

```
handoffs__register-2026-11-06.md
search_results__smith-family.md
reference__ledger-rules.md
research__naturalization-records.md
design__import-pipeline.md
```

---

## Why a prefix

A Project's docs are a flat list. A prefix makes the type visible in that
list and lets `lindakit` sort archived docs into `archive/<type>/` by
reading the name alone. A brand-new category needs no config: use a new
prefix and it gets its own folder.

Because archived files keep their prefixed names, restoring one to the
Project is a copy, and it comes back already named correctly.

---

## Standard types

Use these where they fit. Add your own freely.

| Prefix | What it is | Default |
|---|---|---|
| `handoffs` | session handoffs and summaries | archive (keep if recent) |
| `design` | design docs, plans, specs | archive; route to `docs/roadmap/` |
| `rules` | always-true rules and conventions for Claude | keep; route to `.claude/rules/` |
| `reference` | indexes, inventories, lookups | keep |
| `research` | working notes the project draws on | keep |
| `search_results` | saved results of searches | archive |
| `changedocs` | BEFORE/AFTER change documents | archive |
| `tests` | test notes and plans | archive |
| `prompts` | reusable prompts | archive |

### Rules docs

`rules` docs (`project_rules.md`, `github_rules.md`, `sql_conventions.md`)
are the opposite of everything else: they are never archived away. They
follow Claude Code's own layout, where every markdown file in
`.claude/rules/` loads automatically alongside `CLAUDE.md`.

- **Repo-specific rules** live in the repo's `.claude/rules/`. That is the
  source of truth; the Claude Project holds a copy.
- **Rules for every repo** live once in `~/.claude/rules/`, not in each
  repo.
- The Project copy is still needed for claude.ai, which cannot see the
  repo. Copy, never move.
- Existing names such as `project_rules.md` need not change: the
  `rules` type matches `rules` and `conventions` in a name, so they sort
  as `rules` without a prefix. Procedures (step-by-step workflows) are not
  rules; those belong in skills, not here.

A type's default decision and route come from the repo's
`docs/context/lindakit.yaml`. The prefix alone is enough to sort a doc; the
yaml only decides what happens to it.

---

## Unprefixed and legacy names

`lindakit` resolves a doc's type in this order:

1. Any prefix before `__`. A type listed in `lindakit.yaml` adds a default
   decision and route; an unlisted prefix still gets its own folder and the
   built-in default (archive).
2. A regex match from the `types:` list in `lindakit.yaml` (this is how
   older, unprefixed names still sort).
3. Otherwise `misc`.

Nothing is ever dropped for lack of a prefix. `lindakit rename` (planned)
will propose prefixed names for existing docs as a dry run, apply them with
`git mv`, and write an old-name to new-name map to commit alongside.

---

## Notes for Claude

When creating or saving a doc into a Project that follows this convention,
name it `<type>__<name>.md` using a type from the table above, or a new one
if none fits. Do not put a doc in `misc`.
