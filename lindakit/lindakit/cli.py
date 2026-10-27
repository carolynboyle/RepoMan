# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
lindakit CLI entry point.

Usage:
    lindakit export   [EXPORT_JSON]   — summarize an export file
    lindakit review   [EXPORT_JSON]   — interactive keep/archive/delete review
    lindakit keepers  [REVIEW_JSON]   — generate keepers.json from review
    lindakit archive  [EXPORT_JSON]   — organize archive files into subfolders
"""

import click
from lindakit import __version__


@click.group()
@click.version_option(__version__, prog_name="lindakit")
def main():
    """lindakit — Claude project context lifecycle tools."""


@main.command()
@click.argument("export_json", default="export.json", metavar="EXPORT_JSON")
def export(export_json: str):
    """Summarize an export file from withLinda."""
    from lindakit.export import ExportSummary
    summary = ExportSummary(export_json)
    summary.print()


@main.command()
@click.argument("export_json", default="export.json", metavar="EXPORT_JSON")
@click.option(
    "--output", "-o",
    default="review.json",
    help="Path to write the review decision file [default: review.json]"
)
def review(export_json: str, output: str):
    """Interactively review each doc: keep, archive, or delete."""
    from lindakit.review import ReviewSession
    session = ReviewSession(export_json, output)
    session.run()


@main.command()
@click.argument("review_json", default="review.json", metavar="REVIEW_JSON")
@click.option(
    "--output", "-o",
    default="keepers.json",
    help="Path to write the keepers file [default: keepers.json]"
)
def keepers(review_json: str, output: str):
    """Generate keepers.json for Linda Import from a completed review."""
    from lindakit.keepers import KeepersBuilder
    builder = KeepersBuilder(review_json, output)
    builder.build()


@main.command()
@click.argument("export_json", default="export.json", metavar="EXPORT_JSON")
@click.option(
    "--output-dir", "-d",
    default="archive",
    help="Directory to write organized archive files [default: ./archive]"
)
def archive(export_json: str, output_dir: str):
    """Organize archived docs into subfolders by type."""
    from lindakit.archive import ArchiveOrganizer
    organizer = ArchiveOrganizer(export_json, output_dir)
    organizer.organize()
