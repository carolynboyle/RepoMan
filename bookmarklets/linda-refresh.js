javascript:(async () => {
  // repo_man — Claude project context lifecycle tools
  // Copyright (C) 2026 Carolyn Boyle
  // SPDX-License-Identifier: AGPL-3.0-or-later
  //
  // Linda Refresh — Prune all current docs, then Import from a keepers JSON.
  // Combines linda-prune + linda-import in one bookmarklet.
  // Run from any page inside claude.ai/project/{projectId}/...
  //
  // Order of events, so a cancelled step never leaves the Project empty:
  //   1. List the current docs (read only).
  //   2. You choose and the tool checks the keepers file.
  //   3. You confirm the delete and the import.
  //   4. Only then are docs deleted, then the keepers imported.

  // --- Parse org and project IDs ---
  let orgId, projectId;

  try {
    const bootstrap = await fetch('/api/bootstrap', { credentials: 'include' })
      .then(r => r.json());
    orgId = bootstrap?.account?.memberships?.[0]?.organization?.uuid
         || bootstrap?.organizations?.[0]?.uuid;
  } catch (e) {
    alert('Linda Refresh: could not detect org ID. Are you on claude.ai?');
    return;
  }

  const projMatch = location.href.match(/\/project\/([0-9a-f-]{36})/);
  if (!projMatch) {
    alert('Linda Refresh: navigate to a Claude Project page first.');
    return;
  }
  projectId = projMatch[1];

  if (!orgId || !projectId) {
    alert('Linda Refresh: could not detect org or project ID.');
    return;
  }

  const apiBase = `/api/organizations/${orgId}/projects/${projectId}/docs`;

  // --- Progress overlay ---
  const overlay = document.createElement('div');
  overlay.style.cssText = [
    'position:fixed', 'top:20px', 'right:20px', 'z-index:999999',
    'background:#1a1a2e', 'color:#e0e0e0', 'padding:16px 20px',
    'border-radius:8px', 'font-family:monospace', 'font-size:13px',
    'min-width:300px', 'box-shadow:0 4px 20px rgba(0,0,0,0.5)',
    'border:1px solid #444'
  ].join(';');
  overlay.innerHTML = '<b>🔄 Linda Refresh</b><br><span id="lr-status">Fetching docs…</span><br>';
  document.body.appendChild(overlay);

  const status = () => document.getElementById('lr-status');
  const close = (ms) => setTimeout(() => overlay.remove(), ms);

  // ============================================================
  // Step 1 — List current docs (read only)
  // ============================================================
  let docs;
  try {
    const res = await fetch(apiBase, { credentials: 'include' });
    if (!res.ok) throw new Error(`GET docs: ${res.status}`);
    docs = await res.json();
  } catch (err) {
    status().textContent = `Error: ${err.message}`;
    console.error('Linda Refresh:', err);
    close(6000);
    return;
  }

  // ============================================================
  // Step 2 — Choose the keepers file (a real click, so the browser
  // is certain to open the picker)
  // ============================================================
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json,application/json';
  input.style.display = 'none';
  document.body.appendChild(input);

  const choose = document.createElement('button');
  choose.textContent = 'Choose keepers.json…';
  choose.style.cssText = 'margin-top:10px;padding:6px 12px;cursor:pointer;';
  overlay.appendChild(choose);

  const cancel = document.createElement('button');
  cancel.textContent = 'Cancel';
  cancel.style.cssText = 'margin:10px 0 0 8px;padding:6px 12px;cursor:pointer;';
  overlay.appendChild(cancel);

  const finish = (message, ms) => {
    status().textContent = message;
    input.remove();
    choose.remove();
    cancel.remove();
    close(ms);
  };

  status().textContent =
    `The Project has ${docs.length} doc(s). Nothing is deleted yet. ` +
    'Choose the keepers file first.';

  cancel.addEventListener('click', () => finish('Cancelled. Nothing was deleted.', 3000));
  choose.addEventListener('click', () => input.click());

  input.addEventListener('change', async () => {
    const file = input.files[0];
    if (!file) {
      return;
    }

    let keepers;
    try {
      keepers = JSON.parse(await file.text());
    } catch (e) {
      finish(`Keepers file is not valid JSON: ${e.message}. Nothing was deleted.`, 8000);
      return;
    }

    if (!Array.isArray(keepers) || keepers.length === 0) {
      finish('Keepers file is empty or not an array. Nothing was deleted.', 8000);
      return;
    }

    const bad = keepers.filter(k => !k.file_name || !k.content);
    if (bad.length > 0) {
      finish(`${bad.length} keeper(s) lack a file_name or content. Nothing was deleted.`, 8000);
      return;
    }

    // ==========================================================
    // Step 3 — Confirm
    // ==========================================================
    const names = keepers.slice(0, 8).map(k => k.file_name).join('\n');
    const more = keepers.length > 8 ? `\n…and ${keepers.length - 8} more` : '';
    const ok = confirm(
      `Delete ${docs.length} doc(s) from this Project, then import ` +
      `${keepers.length} doc(s)?\n\nTo import:\n${names}${more}` +
      '\n\nThe delete cannot be undone.'
    );
    if (!ok) {
      finish('Cancelled. Nothing was deleted.', 3000);
      return;
    }

    choose.remove();
    cancel.remove();

    // ==========================================================
    // Step 4a — Prune
    // ==========================================================
    let deleted = 0, failed = 0;
    for (const doc of docs) {
      const del = await fetch(`${apiBase}/${doc.uuid}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (del.ok) deleted++;
      else {
        failed++;
        console.warn('Linda Refresh (prune): failed', doc.uuid, del.status);
      }
      status().textContent = `Deleting… ${deleted + failed}/${docs.length}`;
    }

    if (failed > 0) {
      finish(
        `Stopped: ${failed} doc(s) could not be deleted (see console). ` +
        'Nothing was imported.', 10000
      );
      return;
    }

    // ==========================================================
    // Step 4b — Import
    // ==========================================================
    let imported = 0, importFailed = 0;
    for (const doc of keepers) {
      try {
        const res = await fetch(apiBase, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_name: doc.file_name, content: doc.content })
        });
        if (res.ok) imported++;
        else {
          importFailed++;
          console.warn('Linda Refresh (import): failed', doc.file_name, res.status);
        }
      } catch (e) {
        importFailed++;
        console.error('Linda Refresh (import):', doc.file_name, e);
      }

      status().textContent = `Importing… ${imported + importFailed}/${keepers.length}`;
    }

    finish(
      `✓ Refresh complete. Deleted ${deleted}, imported ${imported}` +
      (importFailed ? `, ${importFailed} import(s) failed (see console)` : '') + '.',
      8000
    );
  });
})();
