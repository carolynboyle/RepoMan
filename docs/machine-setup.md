# Machine Setup: Global File Paths

Where things live on every machine (laptops, Proxmox VMs, the mini). Paths
below are the same everywhere, because shared Claude rules and other tooling
refer to them by `~`-relative path.

---

## The rule

All repos live in `~/projects/`, one folder per repo, named exactly like
the repo (including capitalization).

```
~/projects/
  RepoMan/
  curator/
  seanchai/
  steward/
```

Capitalization matters. macOS is case-insensitive and Linux is not, so
`~/projects/repoman` works on a Mac and fails on a VM. Use the repo's
real name: `RepoMan`, not `repoman`.

---

## New machine checklist

1. Create the folder if it is not there:

   ```
   mkdir -p ~/projects
   ```

2. Clone the repos you need into it:

   ```
   cd ~/projects
   git clone https://github.com/carolynboyle/RepoMan.git
   git clone https://github.com/carolynboyle/curator.git
   git clone https://github.com/carolynboyle/seanchai.git
   git clone https://github.com/carolynboyle/steward.git
   ```

   Seanchai is private, so it needs GitHub authentication.

3. Create `~/.claude/` and put the shared-rule imports in
   `~/.claude/CLAUDE.md`, one per line (see below).

4. Start Claude Code and check `/context`: every imported rules file
   should be listed. A file that is missing from the list is skipped
   silently, so this check is the only way to know.

5. Run `git pull` in each repo before relying on it. A clone that exists
   but is behind loads the old rules without any warning.

---

## Shared Claude rules

Rules that apply to every repo live once, in RepoMan, and are pulled in by
import from the user-level `~/.claude/CLAUDE.md`:

```
@~/projects/RepoMan/docs/rules/project_rules.md
@~/projects/RepoMan/docs/rules/github_rules.md
```

Notes:

- The import path only works if RepoMan is cloned at the path above.
- The user-level file is used so Claude Code does not show the
  external-import approval prompt that project-level files trigger.
- Repo-specific rules go in that repo's `.claude/rules/` and are committed
  with the repo.
- The claude.ai Projects (Curator, seanchaí) cannot see any of this.
  They still need the rules uploaded as project docs.

**Status:** the `@~/` import setup is designed but has not been tested on
a real machine. Test on one machine and then a second before relying on it.
The shared files are not yet in `RepoMan/docs/rules/`.

---

## Other machine facts

Add anything else that must be identical across machines here (editor,
Python version, shell, SSH key setup), so the next machine gets built the
same way.
