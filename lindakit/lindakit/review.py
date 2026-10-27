# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
ReviewSession — interactive keep/archive/delete review of an export.

For each doc, shows the filename, type hint, word count, and a content
preview, then prompts: [k]eep / [a]rchive / [d]elete / [s]kip / [q]uit.

Decisions are written to a review JSON file:
  [
    {
      "file_name": "...",
      "content": "...",
      "uuid": "...",
      "decision": "keep" | "archive" | "delete" | "skip"
    },
    ...
  ]

Re-running review on a partially-reviewed file resumes where you left off
(skips docs that already have a decision other than "skip").
"""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from lindakit.export import ExportSummary


DECISIONS = {
    'k': 'keep',
    'a': 'archive',
    'd': 'delete',
    's': 'skip',
    'q': 'quit',
}


class ReviewSession:
    """Interactive review of export docs."""

    def __init__(self, export_path: str, output_path: str):
        self.export_path = Path(export_path)
        self.output_path = Path(output_path)
        self.summary = ExportSummary(export_path)
        self.decisions: list[dict] = []
        self._load_existing()

    def _load_existing(self):
        """Load any existing decisions so we can resume."""
        if self.output_path.exists():
            with self.output_path.open(encoding='utf-8') as f:
                self.decisions = json.load(f)
        else:
            self.decisions = []

    def _find_existing(self, file_name: str) -> dict | None:
        for d in self.decisions:
            if d.get('file_name') == file_name:
                return d
        return None

    def _save(self):
        with self.output_path.open('w', encoding='utf-8') as f:
            json.dump(self.decisions, f, indent=2, ensure_ascii=False)

    def run(self):
        """Run the interactive review loop."""
        console = Console()
        docs = self.summary.docs
        total = len(docs)

        from datetime import date
        current_month = date.today().strftime('%Y-%m')

        console.print(f"\n[bold]lindakit review[/bold] — {self.export_path}")
        console.print(f"[dim]{total} docs. Decisions saved to {self.output_path}[/dim]")
        console.print("[dim]k=keep  a=archive  d=delete  s=skip  q=quit[/dim]\n")

        for i, doc in enumerate(docs, 1):
            name = doc.get('file_name', f'(doc {i})')
            content = doc.get('content', '')
            kind = self.summary.classify(doc)
            words = len(content.split())
            stale = self.summary.is_stale_handoff(doc, current_month)

            # Skip already-decided docs (non-skip decisions)
            existing = self._find_existing(name)
            if existing and existing.get('decision') not in (None, 'skip'):
                console.print(
                    f"[dim][{i}/{total}] {name} → already {existing['decision']}[/dim]"
                )
                continue

            # Preview: first 300 chars
            preview = content[:300].replace('\n', ' ')
            if len(content) > 300:
                preview += '…'

            # Build hint line
            hints = [kind]
            if stale:
                hints.append('[yellow]stale[/yellow]')
            hint_str = ', '.join(hints)

            console.print(Panel(
                f"[bold]{name}[/bold]\n"
                f"[dim]{hint_str} · {words} words[/dim]\n\n"
                f"{preview}",
                title=f"[cyan]{i}/{total}[/cyan]",
                expand=False
            ))

            while True:
                raw = Prompt.ask(
                    "[bold]Decision[/bold] [dim](k/a/d/s/q)[/dim]",
                    default='s'
                ).strip().lower()

                if raw in DECISIONS:
                    decision = DECISIONS[raw]
                    break
                console.print("[red]Enter k, a, d, s, or q[/red]")

            if decision == 'quit':
                console.print(f"\n[yellow]Quit. {i-1} reviewed, "
                              f"{total - i + 1} remaining.[/yellow]")
                self._save()
                return

            # Update or append
            if existing:
                existing['decision'] = decision
            else:
                self.decisions.append({
                    'file_name': name,
                    'content': doc.get('content', ''),
                    'uuid': doc.get('uuid', ''),
                    'decision': decision,
                })

            self._save()
            console.print(f"[green]→ {decision}[/green]\n")

        # Summary
        from collections import Counter
        counts = Counter(d.get('decision') for d in self.decisions)
        console.print("\n[bold]Review complete.[/bold]")
        for decision, count in sorted(counts.items()):
            console.print(f"  {decision:<10} {count}")
        console.print(f"\nDecisions saved to [cyan]{self.output_path}[/cyan]")
        console.print("Run [bold]lindakit keepers[/bold] to generate keepers.json\n")
