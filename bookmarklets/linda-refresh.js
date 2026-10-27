javascript:(async () => {
  // repo_man — Claude project context lifecycle tools
  // Copyright (C) 2026 Carolyn Boyle
  // SPDX-License-Identifier: AGPL-3.0-or-later
  //
  // Linda Refresh — Prune all current docs, then Import from a keepers JSON.
  // Combines linda-prune + linda-import in one bookmarklet.
  // Run from any page inside claude.ai/project/{projectId}/...

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
  overlay.innerHTML = '<b>🔄 Linda Refresh</b><br><span id="lr-status">Phase 1/2: Fetching docs to prune…</span>';
  document.body.appendChild(overlay);

  const status = () => document.getElementById('lr-status');

  // ============================================================
  // PHASE 1 — Prune
  // ============================================================
  try {
    const res = await fetch(apiBase, { credentials: 'include' });
    if (!res.ok) throw new Error(`GET docs: ${res.status}`);
    const docs = await res.json();

    if (docs && docs.length > 0) {
      status().textContent = `Phase 1/2: Deleting ${docs.length} doc(s)…`;

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
        status().textContent = `Phase 1/2: Deleting… ${deleted + failed}/${docs.length}`;
      }

      status().textContent = `Phase 1/2 done: deleted ${deleted}` +
        (failed ? `, ${failed} failed` : '') + '. Choose keepers…';
    } else {
      status().textContent = 'Phase 1/2: Nothing to prune. Choose keepers…';
    }
  } catch (err) {
    status().textContent = `Prune error: ${err.message}`;
    console.error('Linda Refresh (prune):', err);
    setTimeout(() => overlay.remove(), 6000);
    return;
  }

  // ============================================================
  // PHASE 2 — Import
  // ============================================================
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json,application/json';
  input.style.display = 'none';
  document.body.appendChild(input);

  input.addEventListener('change', async () => {
    const file = input.files[0];
    if (!file) {
      status().textContent = 'No file selected — refresh aborted after prune.';
      setTimeout(() => overlay.remove(), 4000);
      input.remove();
      return;
    }

    let keepers;
    try {
      const text = await file.text();
      keepers = JSON.parse(text);
    } catch (e) {
      status().textContent = `Phase 2 JSON error: ${e.message}`;
      setTimeout(() => overlay.remove(), 6000);
      input.remove();
      return;
    }

    if (!Array.isArray(keepers) || keepers.length === 0) {
      status().textContent = 'Keepers file empty — nothing imported.';
      setTimeout(() => overlay.remove(), 4000);
      input.remove();
      return;
    }

    status().textContent = `Phase 2/2: Importing ${keepers.length} doc(s)…`;

    let imported = 0, failed = 0;
    for (const doc of keepers) {
      if (!doc.file_name || !doc.content) {
        console.warn('Linda Refresh (import): skipping', doc);
        failed++;
        continue;
      }

      try {
        const res = await fetch(apiBase, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_name: doc.file_name, content: doc.content })
        });
        if (res.ok) imported++;
        else {
          failed++;
          console.warn('Linda Refresh (import): failed', doc.file_name, res.status);
        }
      } catch (e) {
        failed++;
        console.error('Linda Refresh (import):', doc.file_name, e);
      }

      status().textContent = `Phase 2/2: Importing… ${imported + failed}/${keepers.length}`;
    }

    status().textContent = `✓ Refresh complete. Imported ${imported}` +
      (failed ? `, ${failed} failed (see console)` : '') + '.';

    setTimeout(() => overlay.remove(), 6000);
    input.remove();
  });

  input.click();
})();
