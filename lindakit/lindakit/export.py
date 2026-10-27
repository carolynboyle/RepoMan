# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
ExportSummary — parse and display an export JSON from withLinda.

The export format (as produced by withLinda's bookmarklet) is a JSON array:
  [
    { "file_name": "...", "content": "...", "uuid": "..." },
    ...
  ]

uuid may or may not be present depending on withLinda version.
"""

import json
import re
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import print as rprint


class ExportSummary:
    """Parse and summarize a withLinda export file."""

    # Filename patterns for auto-classification hints
    HANDOFF_PATTERN = re.compile(
        r'handoff.*\d{4}-\d{2}-\d{2}', re.IGNORECASE
    )
    DESIGN_PATTERN = re.compile(r'^DESIGN_|_design\.', re.IGNORECASE)
    CHANGEDOC_PATTERN = re.compile(r'changedoc|change_doc|changeset', re.IGNORECASE)
    TEST_PATTERN = re.compile(r'^test_|_test\.', re.IGNORECASE)
    CONFIG_PATTERN = re.compile(r'config|settings|rules|conventions', re.IGNORECASE)

    def __init__(self, path: str):
        self.path = Path(path)
        self.docs: list[dict] = []
        self._load()

    def _load(self):
        with self.path.open(encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"{self.path} does not contain a JSON array")

        self.docs = data

    def classify(self, doc: dict) -> str:
        """Heuristic classification for a doc entry."""
        name = doc.get('file_name', '')
        if self.HANDOFF_PATTERN.search(name):
            return 'handoff'
        if self.DESIGN_PATTERN.search(name):
            return 'design'
        if self.CHANGEDOC_PATTERN.search(name):
            return 'changedoc'
        if self.TEST_PATTERN.search(name):
            return 'test'
        if self.CONFIG_PATTERN.search(name):
            return 'config/ref'
        return 'other'

    def is_stale_handoff(self, doc: dict, current_month: str) -> bool:
        """
        Return True if this looks like a handoff from before current_month.
        current_month: 'YYYY-MM' string.
        """
        name = doc.get('file_name', '')
        date_match = re.search(r'(\d{4}-\d{2})-\d{2}', name)
        if date_match and self.HANDOFF_PATTERN.search(name):
            doc_month = date_match.group(1)
            return doc_month < current_month
        return False

    def print(self):
        """Print a summary table to the console."""
        from datetime import date
        current_month = date.today().strftime('%Y-%m')

        console = Console()
        console.print(f"\n[bold]lindakit export[/bold] — {self.path}")
        console.print(f"[dim]{len(self.docs)} docs in export[/dim]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("File name", min_width=30)
        table.add_column("Type", width=12)
        table.add_column("Words", width=8, justify="right")
        table.add_column("Note", style="dim")

        for i, doc in enumerate(self.docs, 1):
            name = doc.get('file_name', '(no name)')
            content = doc.get('content', '')
            words = len(content.split())
            kind = self.classify(doc)
            note = ''
            if kind == 'handoff' and self.is_stale_handoff(doc, current_month):
                note = 'stale (pre-current-month)'

            table.add_row(str(i), name, kind, str(words), note)

        console.print(table)

        # Summary counts
        from collections import Counter
        counts = Counter(self.classify(d) for d in self.docs)
        console.print("\n[bold]By type:[/bold]")
        for kind, count in sorted(counts.items()):
            console.print(f"  {kind:<14} {count}")

        stale = sum(
            1 for d in self.docs
            if self.is_stale_handoff(d, current_month)
        )
        if stale:
            console.print(f"\n[yellow]{stale} stale handoff(s) detected[/yellow]")
        console.print()
