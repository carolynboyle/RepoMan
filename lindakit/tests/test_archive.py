# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lindakit.archive.ArchiveOrganizer."""

import json

import pytest

from lindakit.archive import ArchiveOrganizer


def make_review(tmp_path, docs):
    path = tmp_path / 'review.json'
    path.write_text(json.dumps(docs), encoding='utf-8')
    return path


def doc(name, content='body', uuid='', decision='archive'):
    return {'file_name': name, 'content': content, 'uuid': uuid,
            'decision': decision}


def archived_files(out_dir):
    return sorted(p.relative_to(out_dir).as_posix()
                  for p in out_dir.rglob('*') if p.is_file())


@pytest.mark.parametrize('name, expected', [
    ('plain.md', 'plain.md'),
    ('claude/foo.md', 'claude_foo.md'),
    ('a/b/c.md', 'a_b_c.md'),
    ('win\\path.md', 'win_path.md'),
    ('../escape.md', '.._escape.md'),
    ('', 'unnamed.md'),
    ('..', 'unnamed.md'),
])
def test_safe_name_is_always_a_single_file_name(name, expected):
    assert ArchiveOrganizer.safe_name(name) == expected


def test_name_with_slash_does_not_crash_or_nest(tmp_path):
    review = make_review(tmp_path, [doc('claude/foo.md', 'A')])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    assert archived_files(out) == ['misc/claude_foo.md']


def test_docs_are_sorted_into_typed_subfolders(tmp_path):
    review = make_review(tmp_path, [
        doc('session-handoff-2026-10-01.md'),
        doc('DESIGN_widget.md'),
        doc('random-notes.md'),
    ])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    assert archived_files(out) == [
        'design/DESIGN_widget.md',
        'handoffs/session-handoff-2026-10-01.md',
        'misc/random-notes.md',
    ]


def test_only_docs_marked_archive_are_written(tmp_path):
    review = make_review(tmp_path, [
        doc('a.md', decision='archive'),
        doc('b.md', decision='keep'),
        doc('c.md', decision='delete'),
    ])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    assert archived_files(out) == ['misc/a.md']


def test_same_name_different_content_keeps_both(tmp_path):
    review = make_review(tmp_path, [
        doc('notes.md', 'one', uuid='11111111-aaaa'),
        doc('notes.md', 'two', uuid='22222222-bbbb'),
    ])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    assert archived_files(out) == ['misc/notes-22222222.md', 'misc/notes.md']
    assert (out / 'misc' / 'notes.md').read_text(encoding='utf-8') == 'one'
    assert (out / 'misc' / 'notes-22222222.md').read_text(encoding='utf-8') == 'two'


def test_collision_without_uuid_tags_with_content_hash(tmp_path):
    review = make_review(tmp_path, [doc('notes', 'one'), doc('notes', 'two')])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    files = archived_files(out)
    assert 'misc/notes' in files
    assert len(files) == 2


def test_identical_copy_is_written_once(tmp_path):
    review = make_review(tmp_path, [
        doc('notes.md', 'same', uuid='u1'),
        doc('notes.md', 'same', uuid='u2'),
    ])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    assert archived_files(out) == ['misc/notes.md']


def test_running_twice_changes_nothing(tmp_path):
    review = make_review(tmp_path, [
        doc('notes.md', 'one', uuid='11111111-aaaa'),
        doc('notes.md', 'two', uuid='22222222-bbbb'),
    ])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()
    first = archived_files(out)
    ArchiveOrganizer(str(review), str(out)).organize()

    assert archived_files(out) == first


def test_nothing_marked_archive_writes_nothing(tmp_path):
    review = make_review(tmp_path, [doc('a.md', decision='keep')])
    out = tmp_path / 'arc'

    ArchiveOrganizer(str(review), str(out)).organize()

    assert not out.exists()
