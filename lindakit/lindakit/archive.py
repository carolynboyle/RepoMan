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
"""

import json
import re
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


class ArchiveOrganizer:
    """Organize archived docs from a review file into typed subfolders."""

    def __init__(self, review_path: str, output_dir: str):
        self.review_path = Path(review_path)
        self.output_dir = Path(output_dir)

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
        for doc in archived:
            name = doc.get('file_name', 'unknown.md')
            content = doc.get('content', '')
            kind = ExportSummary.classify(dummy_summary, doc)
            subfolder = SUBFOLDER_MAP.get(kind, 'misc')

            dest_dir = self.output_dir / subfolder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / name

            dest.write_text(content, encoding='utf-8')
            table.add_row(name, subfolder)
            written += 1

        console.print(f"\n[bold]lindakit archive[/bold] — {self.output_dir}/")
        console.print(table)
        console.print(
            f"\n[green]{written} file(s)[/green] written to "
            f"[cyan]{self.output_dir}/[/cyan]\n"
        )
