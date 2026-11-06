# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for lindakit.review.ReviewSession."""

import json

from lindakit.review import ReviewSession


def write_export(tmp_path, docs):
    path = tmp_path / 'export.json'
    path.write_text(json.dumps(docs), encoding='utf-8')
    return path


def answer_with(monkeypatch, answers):
    """Make Prompt.ask return the given answers in order; return the asked list."""
    pending = list(answers)
    asked = []

    def fake_ask(*args, **kwargs):
        asked.append(args)
        return pending.pop(0)

    monkeypatch.setattr('lindakit.review.Prompt.ask', fake_ask)
    return asked


def saved(path):
    return json.loads(path.read_text(encoding='utf-8'))


def test_every_doc_is_reviewed_and_saved(tmp_path, monkeypatch):
    export = write_export(tmp_path, [
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1'},
        {'file_name': 'b.md', 'content': 'B', 'uuid': 'u2'},
    ])
    out = tmp_path / 'review.json'
    answer_with(monkeypatch, ['k', 'a'])

    ReviewSession(str(export), str(out)).run()

    assert [(d['file_name'], d['decision']) for d in saved(out)] == [
        ('a.md', 'keep'), ('b.md', 'archive')]


def test_docs_with_the_same_name_are_both_reviewed(tmp_path, monkeypatch):
    export = write_export(tmp_path, [
        {'file_name': 'notes.md', 'content': 'one', 'uuid': 'u2'},
        {'file_name': 'notes.md', 'content': 'two', 'uuid': 'u3'},
    ])
    out = tmp_path / 'review.json'
    asked = answer_with(monkeypatch, ['k', 'a'])

    ReviewSession(str(export), str(out)).run()

    assert len(asked) == 2
    assert [(d['uuid'], d['decision']) for d in saved(out)] == [
        ('u2', 'keep'), ('u3', 'archive')]


def test_resume_skips_docs_already_decided(tmp_path, monkeypatch):
    export = write_export(tmp_path, [
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1'},
        {'file_name': 'b.md', 'content': 'B', 'uuid': 'u2'},
    ])
    out = tmp_path / 'review.json'
    out.write_text(json.dumps([
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1', 'decision': 'keep'},
    ]), encoding='utf-8')
    asked = answer_with(monkeypatch, ['a'])

    ReviewSession(str(export), str(out)).run()

    assert len(asked) == 1
    assert [(d['uuid'], d['decision']) for d in saved(out)] == [
        ('u1', 'keep'), ('u2', 'archive')]


def test_resume_revisits_skipped_docs(tmp_path, monkeypatch):
    export = write_export(tmp_path, [
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1'},
    ])
    out = tmp_path / 'review.json'
    out.write_text(json.dumps([
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1', 'decision': 'skip'},
    ]), encoding='utf-8')
    answer_with(monkeypatch, ['d'])

    ReviewSession(str(export), str(out)).run()

    assert [d['decision'] for d in saved(out)] == ['delete']


def test_docs_without_a_uuid_fall_back_to_file_name(tmp_path, monkeypatch):
    export = write_export(tmp_path, [{'file_name': 'a.md', 'content': 'A'}])
    out = tmp_path / 'review.json'
    out.write_text(json.dumps([
        {'file_name': 'a.md', 'content': 'A', 'uuid': '', 'decision': 'keep'},
    ]), encoding='utf-8')
    asked = answer_with(monkeypatch, [])

    ReviewSession(str(export), str(out)).run()

    assert asked == []
    assert [d['decision'] for d in saved(out)] == ['keep']


def test_quit_saves_progress_and_stops(tmp_path, monkeypatch):
    export = write_export(tmp_path, [
        {'file_name': 'a.md', 'content': 'A', 'uuid': 'u1'},
        {'file_name': 'b.md', 'content': 'B', 'uuid': 'u2'},
    ])
    out = tmp_path / 'review.json'
    answer_with(monkeypatch, ['k', 'q'])

    ReviewSession(str(export), str(out)).run()

    assert [(d['uuid'], d['decision']) for d in saved(out)] == [('u1', 'keep')]
