# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the lindakit command line."""

import importlib
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from lindakit.cli import main


def test_archive_takes_a_review_file():
    result = CliRunner().invoke(main, ['archive', '--help'])

    assert result.exit_code == 0
    assert 'REVIEW_JSON' in result.output
    assert 'EXPORT_JSON' not in result.output


def test_archive_runs_on_a_review_file(tmp_path):
    review = tmp_path / 'review.json'
    review.write_text(json.dumps([
        {'file_name': 'claude/foo.md', 'content': 'A', 'uuid': 'u1',
         'decision': 'archive'},
    ]), encoding='utf-8')
    out = tmp_path / 'arc'

    result = CliRunner().invoke(main, ['archive', str(review), '-d', str(out)])

    assert result.exit_code == 0
    assert (out / 'misc' / 'claude_foo.md').read_text(encoding='utf-8') == 'A'


def test_build_backend_can_be_imported():
    tomllib = pytest.importorskip('tomllib')
    pyproject = Path(__file__).resolve().parent.parent / 'pyproject.toml'
    data = tomllib.loads(pyproject.read_text(encoding='utf-8'))

    backend = data['build-system']['build-backend']
    module_name, _, attr = backend.partition(':')

    module = importlib.import_module(module_name)
    assert not attr or hasattr(module, attr)
