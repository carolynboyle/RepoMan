# Repo Rules

*Master template — lives in `RepoMan/docs/`. Copy to new repos and fill in `[PROJECT: ...]` slots.*

---

## Philosophy

Good repos are findable, legible, and don't surprise the next person — including future you. A repo that's easy to clone and understand six months later is worth more than one that's clever now. These rules exist so decisions don't have to be remade every time.

---

## Required Root Files

Every repo ships with these at root:

| File | Purpose |
|---|---|
| `README.md` | What this is, how to install/run it, who it's for |
| `LICENSE` | License terms (see [License](#license)) |
| `.gitignore` | Baseline entries from this doc + project-specific additions |
| `claude/project_rules.md` | Code standards and Claude session context |

---

## Baseline .gitignore

Every repo's `.gitignore` includes these entries. Add project-specific entries below them.

```gitignore
# Claude Code — prevents credentials embedded in approved commands from being committed
# Background: https://github.com/carolynboyle/RepoMan/blob/main/docs/repo_rules.md#secrets-discipline
.claude/*.local.json

# Secrets and credentials
.env
.env.local
.env.*
*.pem
*.key
*.p12

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/
.pytest_cache/

# Editor and OS noise
.DS_Store
*.swp
*~

# Logs
*.log
logs/

# [PROJECT: add project-specific entries here]
```

---

## Secrets Discipline

**No secrets in code, config files, or commit history. No exceptions.**

### The Claude Code risk (discovered November 2026)

When Claude Code asks to run a shell command and you pick **Yes, and don't ask again**, it saves the literal command — credentials and all — to `.claude/settings.local.json`. Claude Code adds this file to your *global* gitignore but not the *project's* `.gitignore`. If the project is committed without catching this, those secrets are public.

**Mitigations already in place:**
- `.claude/*.local.json` is in the baseline `.gitignore` above
- If you're unsure whether the file was ever committed in an existing repo, check git history and rotate any credentials that may have been exposed

**General rules:**
- Secrets never in code or config files committed to the repo
- Secrets never in commit messages or PR descriptions
- Use environment variables or a secrets manager (`keyring` in Python for system keychain)
- If a secret was ever committed, treat it as compromised and rotate it — removing it from HEAD is not enough; it remains in history

**Before every push:** scan `git diff origin/main..HEAD` for anything that looks like a password, token, connection string, or key.

---

## Commit Message Format

Conventional Commits structure: `type: subject`, with an optional body.

```
type: short imperative summary (72 chars max)

Optional longer body explaining why, not what.
Wrap at 72 characters.
Reference issues with Fixes #N or See #N.
```

- Subject is imperative mood: "add X", not "added X" or "adds X"
- No period at the end of the subject line
- Type vocabulary is **defined per project** in `claude/project_rules.md`

[PROJECT: define commit types — e.g. standard `feat`, `fix`, `chore`, `docs` or project-specific vocabulary]

---

## License

Default: **AGPL-3.0-or-later** — requires anyone using the code, including as a network service, to publish their source under the same license. This closes the SaaS loophole that standard GPL leaves open.

[PROJECT: confirm license — AGPL-3.0-or-later / MIT / other]

**To apply:**
1. Add a `LICENSE` file at root with the full license text
2. Note the license in `README.md`
3. Optionally add an SPDX identifier to the top of each source file:
   `# SPDX-License-Identifier: AGPL-3.0-or-later`

---

## First-Clone Setup

After cloning a repo, set git identity explicitly — don't rely on global config, which isn't visible in all environments (containers, CI, bridge tools):

```bash
git config user.name "Carolyn Boyle"
git config user.email "carolyn@whycantyoujust.tech"
```

---

## Claude Session Startup

Before touching any code in a Claude session:

1. **Attach or confirm `claude/project_rules.md` is loaded** via the project context
2. **Verify you have the latest file version** before modifying any script — provide either a raw GitHub URL or attach the file directly
3. **Check for a `github_rules.md`** if the session will involve git operations; it describes the push workflow for this machine setup
4. **Reference this file** (`repo_rules.md`) when scaffolding a new repo or doing repo-level housekeeping

---

*This document lives at `RepoMan/docs/repo_rules.md`. When scaffolding a new repo, copy it, fill in `[PROJECT: ...]` slots, and remove this footer.*
