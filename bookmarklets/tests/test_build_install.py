# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for bookmarklets/build_install.py."""

import json
import re
import shutil
import subprocess
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_install import InstallPageBuilder  # noqa: E402

REAL_DIR = Path(__file__).resolve().parent.parent
SAMPLE_JS = (
    "javascript:(async () => {\n"
    "  // a comment with 100% and a # sign\n"
    "  const s = 'héllo — 🗑';\n"
    "  return s;\n"
    "})();\n"
)


def make_dir(tmp_path, entries=None, template=None):
    (tmp_path / "a.js").write_text(SAMPLE_JS, encoding="utf-8")
    (tmp_path / "bookmarklets.json").write_text(
        json.dumps(entries or [
            {"file": "a.js", "label": "A <b>", "description": "Does A & B",
             "destructive": True}]),
        encoding="utf-8")
    (tmp_path / "install.template.html").write_text(
        template or "<body>{{LINKS}}</body>", encoding="utf-8")
    return tmp_path


def hrefs(page):
    return [unescape(h) for h in re.findall(r'href="([^"]+)"', page)]


def test_href_round_trips_to_the_original_code(tmp_path):
    builder = InstallPageBuilder(make_dir(tmp_path))
    href = builder.href("a.js")
    assert href.startswith("javascript:")
    assert "\n" not in href and " " not in href
    assert unquote(href[len("javascript:"):]) == SAMPLE_JS.strip()[len("javascript:"):]


def test_scheme_is_not_doubled(tmp_path):
    href = InstallPageBuilder(make_dir(tmp_path)).href("a.js")
    assert href.count("javascript:") == 1


def test_labels_and_descriptions_are_escaped(tmp_path):
    page = InstallPageBuilder(make_dir(tmp_path)).render()
    assert "A &lt;b&gt;" in page
    assert "Does A &amp; B" in page
    assert "destructive" in page


def test_missing_placeholder_is_an_error(tmp_path):
    builder = InstallPageBuilder(make_dir(tmp_path, template="<body></body>"))
    with pytest.raises(ValueError):
        builder.render()


def test_write_creates_the_file(tmp_path):
    builder = InstallPageBuilder(make_dir(tmp_path))
    out = builder.write(tmp_path / "out.html")
    assert "javascript:" in out.read_text(encoding="utf-8")


def test_real_page_has_one_link_per_bookmarklet():
    builder = InstallPageBuilder(REAL_DIR)
    page = builder.render()
    assert len(hrefs(page)) == len(builder.entries())


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_real_bookmarklets_are_valid_javascript(tmp_path):
    builder = InstallPageBuilder(REAL_DIR)
    for entry in builder.entries():
        href = builder.href(entry["file"])
        code = unquote(href[len("javascript:"):])
        js = tmp_path / entry["file"]
        js.write_text(code, encoding="utf-8")
        result = subprocess.run(["node", "--check", str(js)],
                                capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"{entry['file']}: {result.stderr}"


@pytest.mark.parametrize("name", ["linda-prune.js", "linda-refresh.js"])
def test_nothing_is_deleted_before_a_confirmation(name):
    code = (REAL_DIR / name).read_text(encoding="utf-8")
    assert "confirm(" in code
    assert code.index("confirm(") < code.index("'DELETE'")
