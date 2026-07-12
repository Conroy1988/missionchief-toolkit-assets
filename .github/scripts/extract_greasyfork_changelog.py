#!/usr/bin/env python3

import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

BLOCK_TAGS = {
    "br", "p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
    "section", "article", "blockquote", "pre",
}


class HistoryParser(HTMLParser):
    """Extract top-level version entries from Greasy Fork's History page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.history_depth = None
        self.entry_depth = None
        self.version_depth = None
        self.changelog_depth = None
        self.version_parts = []
        self.changelog_parts = []
        self.entries = []

    @staticmethod
    def classes(attrs):
        return set(dict(attrs).get("class", "").split())

    def handle_starttag(self, tag, attrs):
        classes = self.classes(attrs)
        is_void = tag in VOID_TAGS
        if not is_void:
            self.stack.append(tag)
        depth = len(self.stack) + (1 if is_void else 0)

        if self.history_depth is None:
            if tag == "ul" and "history_versions" in classes:
                self.history_depth = len(self.stack)
            return

        # Only direct child <li> elements of the History list are version entries.
        if self.entry_depth is None and tag == "li" and len(self.stack) == self.history_depth + 1:
            self.entry_depth = len(self.stack)
            self.version_parts = []
            self.changelog_parts = []
            return

        if self.entry_depth is None:
            return

        if self.version_depth is None and "version-number" in classes:
            self.version_depth = len(self.stack)

        if self.changelog_depth is None and "version-changelog" in classes:
            self.changelog_depth = len(self.stack)

        if self.changelog_depth is not None:
            if tag == "br":
                self.changelog_parts.append("\n")
            elif tag == "li":
                self.changelog_parts.append("\n• ")
            elif tag in BLOCK_TAGS and depth > self.changelog_depth:
                self.changelog_parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if self.entry_depth is not None and self.changelog_depth is not None and tag == "br":
            self.changelog_parts.append("\n")

    def handle_endtag(self, tag):
        depth = len(self.stack)

        if self.entry_depth is not None and self.changelog_depth is not None:
            if tag in BLOCK_TAGS and depth > self.changelog_depth:
                self.changelog_parts.append("\n")

        if self.version_depth == depth:
            self.version_depth = None

        if self.changelog_depth == depth:
            self.changelog_depth = None

        if self.entry_depth == depth and tag == "li":
            self.entries.append(("".join(self.version_parts), "".join(self.changelog_parts)))
            self.entry_depth = None
            self.version_depth = None
            self.changelog_depth = None

        if self.history_depth == depth and tag == "ul":
            self.history_depth = None

        if self.stack:
            if self.stack[-1] == tag:
                self.stack.pop()
            elif tag in self.stack:
                reverse_index = self.stack[::-1].index(tag)
                del self.stack[len(self.stack) - reverse_index - 1:]

    def handle_data(self, data):
        if self.entry_depth is None:
            return
        if self.version_depth is not None:
            self.version_parts.append(data)
        if self.changelog_depth is not None:
            self.changelog_parts.append(data)


def clean_text(value):
    value = unescape(value).replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    lines = [line.strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def normalise_version(value):
    match = re.search(r"(?:^|\s)v?([0-9][0-9A-Za-z._+-]*)", clean_text(value))
    return match.group(1).lstrip("vV") if match else None


def main():
    if len(sys.argv) != 4:
        raise SystemExit("Usage: extract_greasyfork_changelog.py VERSION HTML_FILE OUTPUT_FILE")

    target_version = sys.argv[1].strip().lstrip("vV")
    html_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    html = html_path.read_text(encoding="utf-8", errors="replace")

    parser = HistoryParser()
    parser.feed(html)

    if not parser.entries:
        print("No Greasy Fork History entries were found.", file=sys.stderr)
        return 1

    # Greasy Fork sorts History newest first. Only use the latest entry so an
    # older changelog can never be repeated for a newer release.
    latest_version_text, latest_changelog_text = parser.entries[0]
    latest_version = normalise_version(latest_version_text)

    if latest_version != target_version:
        print(
            f"Latest History version is {latest_version or 'unknown'}, expected {target_version}.",
            file=sys.stderr,
        )
        return 1

    changelog = clean_text(latest_changelog_text)

    # Discord embed field values are limited to 1024 characters.
    if len(changelog) > 1000:
        changelog = changelog[:997].rstrip() + "..."

    output_path.write_text(changelog, encoding="utf-8")
    print(
        f"Matched latest Greasy Fork version {target_version}; "
        f"changelog length: {len(changelog)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
