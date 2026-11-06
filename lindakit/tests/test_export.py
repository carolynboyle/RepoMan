# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lindakit.export.ExportSummary."""

import json

import pytest

from lindakit.export import ExportSummary


@pytest.fixture
def summary(tmp_path):
    path = tmp_path / 'export.json'
    path.write_text('[]', encoding='utf-8')
    return ExportSummary(str(path))


@pytest.mark.parametrize('name, kind', [
    ('session-handoff-2026-10-01.md', 'handoff'),
    ('DESIGN_widget.md', 'design'),
    ('changedoc_fix.md', 'changedoc'),
    ('test_plan.md', 'test'),
    ('project_rules.md', 'config/ref'),
    ('random-notes.md', 'other'),
])
def test_classify(summary, name, kind):
    assert summary.classify({'file_name': name}) == kind


def test_handoff_before_current_month_is_stale(summary):
    doc = {'file_name': 'handoff-2026-09-15.md'}
    assert summary.is_stale_handoff(doc, '2026-10')
    assert not summary.is_stale_handoff(doc, '2026-09')


def test_export_must_be_a_json_array(tmp_path):
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps({'not': 'a list'}), encoding='utf-8')
    with pytest.raises(ValueError):
        ExportSummary(str(path))
