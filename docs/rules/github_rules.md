# Claude ↔ GitHub Rules

Written 2026-11-06 after a session lost an hour to a false belief that Claude "can't push." Read this before any git work.

---

## 1. Two separate paths — know which one you're on

| | **Bridge (device_bash)** | **Cloud workspace (Bash)** |
|---|---|---|
| Where | Linux VM on Carolyn's Mac (wcyjl3), connected folders at `$HOME/mnt/<folder>` | Claude's own container, clones at `/home/claude/<repo>` |
| Sees Carolyn's local files | Yes (connected folders only) | No — only what's staged across |
| Reaches GitHub | **No — by design.** Proxy at `localhost:3128` returns 403 for github.com (SSH and HTTPS). Not a network, VPN, Tailscale or app-update problem. | **Yes** — repos attached via `add_repo` with `access: "push"` push over HTTPS |

**All pushes go from the cloud workspace.** A failed push from the bridge is expected and means nothing — never record it as "Carolyn must push from terminal."

---

## 2. Session setup

1. `add_repo` each repo needed, `access: "push"`. Clone into `/home/claude/<repo>` (`git clone --depth 1 …`, generous timeout), then `register_repo_root`.
2. If local files are involved, `device_request_folder_access` for `~/projects/<repo>` (one request, all repos needed).
3. If committing on the Mac, `device_request_delete_permission` for those folders — git needs to delete its own lock/temp files. Without it, commits leave stale `.lock` files.

---

## 3. Standard workflow — edit on the Mac, push from the cloud

Use when the work touches files that exist only on the Mac, or Carolyn wants the Mac copy current without pulling.

1. Edit and commit on the Mac via device_bash (`cd $HOME/mnt/<repo>`).
2. Bundle the new commits:
   `git bundle create .push.bundle origin/main..main`
3. Stage it: `device_stage_files` → lands at `/mnt/user-data/uploads/<repo>/.push.bundle`
4. In the cloud clone (make sure it's at `origin/main` first — `git fetch origin main` if unsure):
   ```bash
   git fetch /mnt/user-data/uploads/<repo>/.push.bundle main:refs/remotes/bundle/main
   git merge --ff-only bundle/main
   git push origin main
   ```
5. Back on the Mac: delete the bundle, then sync the tracking ref so the Mac shows up to date:
   `git update-ref refs/remotes/origin/main <pushed-sha>`
6. Confirm `git status -sb` shows `main...origin/main` with no ahead/behind.

Same commit hash on both sides — no pull needed on the Mac.

If `--ff-only` fails, the cloud clone and the Mac have diverged: stop and tell Carolyn, don't force anything.

---

## 4. Alternative workflow — work in the cloud clone

Use for changes that don't depend on local-only files (e.g. new SQL, docs). Edit, commit and push directly in `/home/claude/<repo>`. Tell Carolyn which repo changed so she can `git pull` on the Mac / VPS.

---

## 5. Git identity

- Per-repo config on the Mac: `user.name = Carolyn Boyle`, `user.email = carolyn@whycantyoujust.tech`. Check with `git config user.email` before committing; fix if missing.
- Commit messages end with the session's Co-Authored-By trailer (GitHub shows "carolynboyle and claude committed").
- Commit vocabulary: `chart` (schema), `trim` (polish), `patch` (bug fix).

---

## 6. Before claiming something can't be done

- Check earlier handoffs and search past chats in this project first. Past sessions pushed to steward, curator and seanchai — capability is established.
- Test the actual path (cloud workspace), not a different one.
- Never write a guess into a handoff as a constraint. If uncertain, write it as an open question.

---

## 7. Hard constraints (unchanged)

- All writes go to GitHub; Carolyn pulls on the VPS — never edit VPS files directly.
- Prefer `main`; few branches. The session can't delete GitHub branches.
- Never force-push.
