javascript:(async () => {
  // repo_man — Claude project context lifecycle tools
  // Copyright (C) 2026 Carolyn Boyle
  // SPDX-License-Identifier: AGPL-3.0-or-later
  //
  // Linda Import — import docs from a keepers JSON file into the current
  // Claude Project. Run from any page inside claude.ai/project/{projectId}/...
  //
  // Keepers JSON format (produced by `lindakit keepers`):
  //   [ { "file_name": "name.md", "content": "..." }, ... ]

  // --- Parse org and project IDs ---
  let orgId, projectId;

  try {
    const bootstrap = await fetch('/api/bootstrap', { credentials: 'include' })
      .then(r => r.json());
    orgId = bootstrap?.account?.memberships?.[0]?.organization?.uuid
         || bootstrap?.organizations?.[0]?.uuid;
  } catch (e) {
    alert('Linda Import: could not detect org ID. Are you on claude.ai?');
    return;
  }

  const projMatch = location.href.match(/\/project\/([0-9a-f-]{36})/);
  if (!projMatch) {
    alert('Linda Import: navigate to a Claude Project page first.');
    return;
  }
  projectId = projMatch[1];

  if (!orgId || !projectId) {
    alert('Linda Import: could not detect org or project ID.');
    return;
  }

  const apiBase = `/api/organizations/${orgId}/projects/${projectId}/docs`;

  // --- Progress overlay ---
  const overlay = document.createElement('div');
  overlay.style.cssText = [
    'position:fixed', 'top:20px', 'right:20px', 'z-index:999999',
    'background:#1a2e1a', 'color:#e0e0e0', 'padding:16px 20px',
    'border-radius:8px', 'font-family:monospace', 'font-size:13px',
    'min-width:280px', 'box-shadow:0 4px 20px rgba(0,0,0,0.5)',
    'border:1px solid #333'
  ].join(';');
  overlay.innerHTML = '<b>📥 Linda Import</b><br><span id="li-status">Choose your keepers.json…</span>';
  document.body.appendChild(overlay);

  const status = () => document.getElementById('li-status');

  // --- File picker ---
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json,application/json';
  input.style.display = 'none';
  document.body.appendChild(input);

  input.addEventListener('change', async () => {
    const file = input.files[0];
    if (!file) {
      status().textContent = 'No file selected.';
      setTimeout(() => overlay.remove(), 3000);
      input.remove();
      return;
    }

    let keepers;
    try {
      const text = await file.text();
      keepers = JSON.parse(text);
    } catch (e) {
      status().textContent = `JSON parse error: ${e.message}`;
      setTimeout(() => overlay.remove(), 5000);
      input.remove();
      return;
    }

    if (!Array.isArray(keepers) || keepers.length === 0) {
      status().textContent = 'Keepers file is empty or not an array.';
      setTimeout(() => overlay.remove(), 5000);
      input.remove();
      return;
    }

    status().textContent = `Importing ${keepers.length} doc(s)…`;

    let imported = 0, failed = 0;
    for (const doc of keepers) {
      if (!doc.file_name || !doc.content) {
        console.warn('Linda Import: skipping entry missing file_name or content', doc);
        failed++;
        continue;
      }

      try {
        const res = await fetch(apiBase, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            file_name: doc.file_name,
            content: doc.content
          })
        });

        if (res.ok) {
          imported++;
        } else {
          failed++;
          console.warn('Linda Import: failed to import', doc.file_name, res.status);
        }
      } catch (e) {
        failed++;
        console.error('Linda Import: error importing', doc.file_name, e);
      }

      status().textContent = `Importing… ${imported + failed}/${keepers.length}`;
    }

    status().textContent = `Done. Imported ${imported}` +
      (failed ? `, ${failed} failed (see console)` : '') + '.';

    setTimeout(() => overlay.remove(), 5000);
    input.remove();
  });

  input.click();
})();
