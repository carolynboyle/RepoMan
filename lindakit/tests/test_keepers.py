# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lindakit.keepers.KeepersBuilder."""

import json

from lindakit.keepers import KeepersBuilder


def test_only_docs_marked_keep_are_written(tmp_path):
    review = tmp_path / 'review.json'
    review.write_text(json.dumps([
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1', 'decision': 'keep'},
        {'file_name': 'b.md', 'content': 'B', 'uuid': 'u2', 'decision': 'archive'},
        {'file_name': 'c.md', 'content': 'C', 'uuid': 'u3', 'decision': 'delete'},
        {'file_name': 'd.md', 'content': 'D', 'uuid': 'u4', 'decision': 'skip'},
    ]), encoding='utf-8')
    out = tmp_path / 'keepers.json'

    KeepersBuilder(str(review), str(out)).build()

    assert json.loads(out.read_text(encoding='utf-8')) == [
        {'file_name': 'a.md', 'content': 'A'}]
