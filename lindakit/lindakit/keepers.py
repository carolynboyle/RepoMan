# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
KeepersBuilder — generate a keepers.json file from a completed review.

keepers.json is the input to the Linda Import bookmarklet:
  [
    { "file_name": "project_rules.md", "content": "..." },
    ...
  ]

Only docs with decision == "keep" are included.
"""

import json
from pathlib import Path

from rich.console import Console


class KeepersBuilder:
    """Build keepers.json from a review file."""

    def __init__(self, review_path: str, output_path: str):
        self.review_path = Path(review_path)
        self.output_path = Path(output_path)

    def build(self):
        console = Console()

        with self.review_path.open(encoding='utf-8') as f:
            decisions = json.load(f)

        keepers = [
            {'file_name': d['file_name'], 'content': d['content']}
            for d in decisions
            if d.get('decision') == 'keep'
        ]

        with self.output_path.open('w', encoding='utf-8') as f:
            json.dump(keepers, f, indent=2, ensure_ascii=False)

        skipped = sum(1 for d in decisions if d.get('decision') == 'skip')
        archived = sum(1 for d in decisions if d.get('decision') == 'archive')
        deleted = sum(1 for d in decisions if d.get('decision') == 'delete')
        unreviewed = sum(
            1 for d in decisions
            if d.get('decision') not in ('keep', 'skip', 'archive', 'delete')
        )

        console.print(f"\n[bold]lindakit keepers[/bold]")
        console.print(f"  keep     {len(keepers)}")
        console.print(f"  archive  {archived}")
        console.print(f"  delete   {deleted}")
        if skipped:
            console.print(f"  skip     {skipped}  [dim](not included)[/dim]")
        if unreviewed:
            console.print(f"  [yellow]unreviewed {unreviewed} (not included)[/yellow]")
        console.print(
            f"\n[cyan]{self.output_path}[/cyan] written — "
            f"ready for Linda Import.\n"
        )
