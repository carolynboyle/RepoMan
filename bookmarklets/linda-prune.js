javascript:(async () => {
  // repo_man — Claude project context lifecycle tools
  // Copyright (C) 2026 Carolyn Boyle
  // SPDX-License-Identifier: AGPL-3.0-or-later
  //
  // Linda Prune — delete all docs from the current Claude Project.
  // Run from any page inside claude.ai/project/{projectId}/...

  // --- Parse org and project UUIDs from page URL ---
  const urlMatch = location.href.match(
    /claude\.ai\/(?:project|chat)\/([0-9a-f-]{36})(?:\/([0-9a-f-]{36}))?/
  );

  // Try the Projects page URL pattern: /project/{projectId}
  const projectPageMatch = location.href.match(
    /claude\.ai\/project\/([0-9a-f-]{36})/
  );

  // Fetch org ID from the bootstrap endpoint
  let orgId, projectId;

  try {
    const bootstrap = await fetch('/api/bootstrap', { credentials: 'include' })
      .then(r => r.json());
    orgId = bootstrap?.account?.memberships?.[0]?.organization?.uuid
         || bootstrap?.organizations?.[0]?.uuid;
  } catch (e) {
    alert('Linda Prune: could not detect org ID. Are you on claude.ai?');
    return;
  }

  // Project ID comes from the URL
  const projMatch = location.href.match(/\/project\/([0-9a-f-]{36})/);
  if (!projMatch) {
    alert('Linda Prune: navigate to a Claude Project page first.');
    return;
  }
  projectId = projMatch[1];

  if (!orgId || !projectId) {
    alert('Linda Prune: could not detect org or project ID.');
    return;
  }

  const apiBase = `/api/organizations/${orgId}/projects/${projectId}/docs`;

  // --- Progress overlay ---
  const overlay = document.createElement('div');
  overlay.style.cssText = [
    'position:fixed', 'top:20px', 'right:20px', 'z-index:999999',
    'background:#1a1a2e', 'color:#e0e0e0', 'padding:16px 20px',
    'border-radius:8px', 'font-family:monospace', 'font-size:13px',
    'min-width:280px', 'box-shadow:0 4px 20px rgba(0,0,0,0.5)',
    'border:1px solid #333'
  ].join(';');
  overlay.innerHTML = '<b>🗑 Linda Prune</b><br><span id="lp-status">Fetching docs…</span>';
  document.body.appendChild(overlay);

  const status = () => document.getElementById('lp-status');

  try {
    // Fetch all docs
    const res = await fetch(apiBase, { credentials: 'include' });
    if (!res.ok) throw new Error(`GET docs: ${res.status}`);
    const docs = await res.json();

    if (!docs || docs.length === 0) {
      status().textContent = 'No docs to delete.';
      setTimeout(() => overlay.remove(), 3000);
      return;
    }

    status().textContent = `Found ${docs.length} doc(s). Deleting…`;

    let deleted = 0, failed = 0;
    for (const doc of docs) {
      const del = await fetch(`${apiBase}/${doc.uuid}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (del.ok) {
        deleted++;
      } else {
        failed++;
        console.warn('Linda Prune: failed to delete', doc.uuid, del.status);
      }
      status().textContent = `Deleting… ${deleted + failed}/${docs.length}`;
    }

    status().textContent = `Done. Deleted ${deleted}` +
      (failed ? `, ${failed} failed (see console)` : '') + '.';

  } catch (err) {
    status().textContent = `Error: ${err.message}`;
    console.error('Linda Prune error:', err);
  }

  setTimeout(() => overlay.remove(), 5000);
})();
