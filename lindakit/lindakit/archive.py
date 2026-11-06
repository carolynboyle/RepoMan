# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
ArchiveOrganizer — write archived docs into organized subfolders.

Reads the review.json (docs with decision == "archive") and writes each
doc's content as a .md file into a typed subfolder:

  archive/
    handoffs/
    design/
    changedocs/
    tests/
    config/
    misc/

Classification uses the same heuristics as ExportSummary.classify().

File names are flattened (a "/" becomes "_") so a name such as
"claude/foo.md" is always a single file. Archiving never overwrites a
different doc: if a file of that name already holds different content, the
new doc is written beside it with a short uuid tag in the name. A doc whose
content is already there, unchanged, is skipped.
"""

import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from lindakit.export import ExportSummary


# Map ExportSummary.classify() values to subfolder names
SUBFOLDER_MAP = {
    'handoff':    'handoffs',
    'design':     'design',
    'changedoc':  'changedocs',
    'test':       'tests',
    'config/ref': 'config',
    'other':      'misc',
}

# Characters of the uuid (or content hash) used to tag a colliding name
TAG_LENGTH = 8


class ArchiveOrganizer:
    """Organize archived docs from a review file into typed subfolders."""

    def __init__(self, review_path: str, output_dir: str):
        self.review_path = Path(review_path)
        self.output_dir = Path(output_dir)

    @staticmethod
    def safe_name(name: str) -> str:
        """Flatten path separators so a doc name is always one file name."""
        flat = name.replace('/', '_').replace('\\', '_').strip()
        if flat in ('', '.', '..'):
            return 'unnamed.md'
        return flat

    @staticmethod
    def _tagged_name(name: str, doc: dict) -> str:
        """Return name with a short uuid (or content hash) tag before the extension."""
        content = doc.get('content', '')
        tag = (doc.get('uuid') or hashlib.sha1(content.encode('utf-8')).hexdigest())
        tag = tag[:TAG_LENGTH]
        if '.' in name:
            stem, ext = name.rsplit('.', 1)
            return f"{stem}-{tag}.{ext}"
        return f"{name}-{tag}"

    @staticmethod
    def _holds(path: Path, content: str) -> bool:
        """True if path exists and already holds exactly this content."""
        return path.exists() and path.read_text(encoding='utf-8') == content

    def _destination(self, dest_dir: Path, name: str, doc: dict) -> Path | None:
        """
        Choose where to write a doc without overwriting a different one.

        Returns None when an identical copy is already there.
        """
        content = doc.get('content', '')
        dest = dest_dir / name
        if not dest.exists():
            return dest
        if self._holds(dest, content):
            return None
        tagged = dest_dir / self._tagged_name(name, doc)
        if self._holds(tagged, content):
            return None
        return tagged

    def organize(self):
        console = Console()

        with self.review_path.open(encoding='utf-8') as f:
            decisions = json.load(f)

        archived = [d for d in decisions if d.get('decision') == 'archive']

        if not archived:
            console.print("[yellow]No docs marked archive — nothing to organize.[/yellow]")
            return

        # We need an ExportSummary classifier but without a file;
        # instantiate it with a dummy and use the class methods directly.
        dummy_summary = ExportSummary.__new__(ExportSummary)

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("File name", min_width=30)
        table.add_column("→ Subfolder", width=14)

        written = 0
        skipped = 0
        for doc in archived:
            name = self.safe_name(doc.get('file_name', 'unknown.md'))
            content = doc.get('content', '')
            kind = ExportSummary.classify(dummy_summary, doc)
            subfolder = SUBFOLDER_MAP.get(kind, 'misc')

            dest_dir = self.output_dir / subfolder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = self._destination(dest_dir, name, doc)

            if dest is None:
                skipped += 1
                continue

            dest.write_text(content, encoding='utf-8')
            table.add_row(dest.name, subfolder)
            written += 1

        console.print(f"\n[bold]lindakit archive[/bold] — {self.output_dir}/")
        console.print(table)
        console.print(
            f"\n[green]{written} file(s)[/green] written to "
            f"[cyan]{self.output_dir}/[/cyan]"
        )
        if skipped:
            console.print(f"[dim]{skipped} identical copy(ies) already there, skipped[/dim]")
        console.print()
