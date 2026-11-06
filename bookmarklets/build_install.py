# repo_man — Claude project context lifecycle tools
# Copyright (C) 2026 Carolyn Boyle
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Build install.html: a page of draggable bookmarklet links.

Each link's href is the bookmarklet source, percent-encoded, so newlines
and // comments survive intact. Nothing is minified and nothing needs to
be pasted into a bookmark by hand.

Standard library only; no virtual environment is needed.

Usage:
    python3 build_install.py            # writes install.html here
    python3 build_install.py OUT.html   # writes to OUT.html
"""

import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

SCHEME = "javascript:"
PLACEHOLDER = "{{LINKS}}"


class InstallPageBuilder:
    """Render install.html from the bookmarklet .js files."""

    def __init__(self, source_dir, manifest="bookmarklets.json",
                 template="install.template.html"):
        self.source_dir = Path(source_dir)
        self.manifest = self.source_dir / manifest
        self.template = self.source_dir / template

    def entries(self):
        """Return the manifest entries, in order."""
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def href(self, js_file):
        """Return a javascript: URL for a bookmarklet source file."""
        code = (self.source_dir / js_file).read_text(encoding="utf-8").strip()
        if code.startswith(SCHEME):
            code = code[len(SCHEME):]
        return SCHEME + quote(code, safe="")

    def link_block(self, entry):
        """Return the HTML for one draggable link and its description."""
        css = "bookmarklet destructive" if entry.get("destructive") else "bookmarklet"
        label = html.escape(entry["label"])
        return (
            f'<div class="bm"><a class="{css}" '
            f'href="{html.escape(self.href(entry["file"]), quote=True)}">'
            f'{label}</a></div>\n'
            f'<p class="desc">{html.escape(entry["description"])}</p>\n'
        )

    def render(self):
        """Return the complete install page as text."""
        links = "".join(self.link_block(e) for e in self.entries())
        page = self.template.read_text(encoding="utf-8")
        if PLACEHOLDER not in page:
            raise ValueError(f"{self.template} has no {PLACEHOLDER} marker")
        return page.replace(PLACEHOLDER, links)

    def write(self, out_path):
        """Write the page to out_path and return the path."""
        out = Path(out_path)
        out.write_text(self.render(), encoding="utf-8")
        return out


def main(argv):
    """Build install.html next to this script, or at the given path."""
    here = Path(__file__).resolve().parent
    out = argv[1] if len(argv) > 1 else here / "install.html"
    path = InstallPageBuilder(here).write(out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main(sys.argv)
