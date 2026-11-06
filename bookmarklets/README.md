# RepoMan Bookmarklets

Browser-side tools for managing claude.ai Project docs, using your
existing browser session for auth (no API keys needed).

---

## Prerequisite: withLinda exporter

Before using RepoMan's bookmarklets, you need the **withLinda
claude-project-knowledge-exporter** to export your current Project docs:

👉 https://github.com/withLinda/claude-project-knowledge-exporter

Install her bookmarklet, run it on your Project page, and save the
exported JSON. That JSON is the input to `lindakit review` and ultimately
to Linda Import.

---

## Installing the bookmarklets

1. Open `bookmarklets/install.html` in your browser (double-click it).
2. Show the bookmarks bar if it is hidden (Ctrl+Shift+B, or Cmd+Shift+B
   on a Mac).
3. Drag each button onto the bar.

Do not paste the `.js` files into a bookmark by hand. Browsers flatten a
pasted URL onto one line, which turns the first `//` comment into the end
of the program.

`install.html` is generated. After editing a `.js` file or
`bookmarklets.json`, rebuild it with `python3 build_install.py` (standard
library only, no virtual environment needed) and commit the result.

---

## The bookmarklets

### Linda Prune (`linda-prune.js`)

**Deletes all docs from the current Project.**

Navigate to any page inside your Claude Project
(`claude.ai/project/{projectId}/...`), then click Linda Prune.

It will:
- Auto-detect your org and project UUIDs from the page URL
- Fetch all current docs from the Project API
- Delete them one by one with a progress overlay
- Report the count when done

⚠️ This is destructive. Run it only after you've exported with withLinda
and have your `keepers.json` ready to re-import.

---

### Linda Import (`linda-import.js`)

**Imports docs from a keepers JSON file into the current Project.**

Navigate to your Claude Project page, then click Linda Import.

It will:
- Inject a file picker into the page
- Read your `keepers.json` (produced by `lindakit keepers`)
- POST each doc to the Project API
- Show progress and report success/failure counts

The keepers JSON format is:
```json
[
  {
    "file_name": "project_rules.md",
    "content": "# Project Rules\n\n..."
  },
  ...
]
```

---

### Linda Refresh (`linda-refresh.js`)

**Prune + Import in one shot.**

Combines Linda Prune and Linda Import: deletes all current docs, then
immediately opens the file picker for your keepers.json.

Use this when you've already done the review and are ready to reset the
context window cleanly.

---

## How the API calls work

All bookmarklets call the claude.ai Projects API directly:

```
GET  /api/organizations/{orgId}/projects/{projectId}/docs
POST /api/organizations/{orgId}/projects/{projectId}/docs
DEL  /api/organizations/{orgId}/projects/{projectId}/docs/{docId}
```

The org and project UUIDs are parsed from the current page URL. Auth is
`credentials: 'include'` — your existing claude.ai session cookie.

No tokens, no keys, no server. Just your browser talking to the API it's
already authenticated with.
