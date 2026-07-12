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
    if len(sys.argv) != 5:
        raise SystemExit(
            "Usage: extract_greasyfork_changelog.py CURRENT_VERSION "
            "PREVIOUS_VERSION HTML_FILE OUTPUT_FILE"
        )

    current_version = sys.argv[1].strip().lstrip("vV")
    previous_version = sys.argv[2].strip().lstrip("vV")
    html_path = Path(sys.argv[3])
    output_path = Path(sys.argv[4])
    html = html_path.read_text(encoding="utf-8", errors="replace")

    parser = HistoryParser()
    parser.feed(html)

    entries = []
    for raw_version, raw_changelog in parser.entries:
        version = normalise_version(raw_version)
        if version:
            entries.append((version, clean_text(raw_changelog)))

    if not entries:
        print("No Greasy Fork History entries were found.", file=sys.stderr)
        return 1

    # Greasy Fork sorts History newest first. Do not process a cached/stale page.
    latest_version = entries[0][0]
    if latest_version != current_version:
        print(
            f"Latest History version is {latest_version}, expected {current_version}.",
            file=sys.stderr,
        )
        return 1

    # Collect every non-empty changelog since the last Discord announcement.
    # This matters when several Greasy Fork versions are published before the
    # scheduled workflow runs. Older, already-announced changelogs are excluded.
    new_changelogs = []
    previous_found = not previous_version

    for version, changelog in entries:
        if previous_version and version == previous_version:
            previous_found = True
            break
        if changelog:
            new_changelogs.append((version, changelog))

    if not previous_found:
        print(
            f"Previously announced version {previous_version} was not found in History.",
            file=sys.stderr,
        )
        return 1

    # Present oldest-to-newest so the Discord summary reads naturally.
    new_changelogs.reverse()
    sections = [f"**v{version}**\n{changelog}" for version, changelog in new_changelogs]
    combined = "\n\n".join(sections)

    # Discord embed field values are limited to 1024 characters.
    if len(combined) > 1000:
        combined = combined[:997].rstrip() + "..."

    output_path.write_text(combined, encoding="utf-8")
    print(
        f"Matched Greasy Fork range {previous_version or 'initial'} -> {current_version}; "
        f"new changelog entries: {len(new_changelogs)}; output length: {len(combined)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
