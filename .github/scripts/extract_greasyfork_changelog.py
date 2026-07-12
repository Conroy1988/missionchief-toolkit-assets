#!/usr/bin/env python3

import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class HistoryParser(HTMLParser):
    BLOCK_TAGS = {"br", "p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6"}
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_history = False
        self.history_ul_depth = 0
        self.in_entry = False
        self.entry_depth = 0
        self.version_depth = 0
        self.changelog_depth = 0
        self.version_parts = []
        self.changelog_parts = []
        self.entries = []

    @staticmethod
    def classes(attrs):
        return set(dict(attrs).get("class", "").split())

    def handle_starttag(self, tag, attrs):
        classes = self.classes(attrs)

        if tag == "ul" and "history_versions" in classes and not self.in_history:
            self.in_history = True
            self.history_ul_depth = 1
            return

        if self.in_history:
            if tag == "ul":
                self.history_ul_depth += 1

            if tag == "li" and not self.in_entry:
                self.in_entry = True
                self.entry_depth = 1
                self.version_parts = []
                self.changelog_parts = []
                return

        if self.in_entry:
            if tag == "li":
                self.entry_depth += 1

            if tag == "span" and "version-number" in classes and self.version_depth == 0:
                self.version_depth = 1
            elif self.version_depth and tag not in self.VOID_TAGS:
                self.version_depth += 1

            if tag == "span" and "version-changelog" in classes and self.changelog_depth == 0:
                self.changelog_depth = 1
            elif self.changelog_depth:
                if tag == "li":
                    self.changelog_parts.append("\n• ")
                elif tag in self.BLOCK_TAGS:
                    self.changelog_parts.append("\n")
                if tag not in self.VOID_TAGS:
                    self.changelog_depth += 1

    def handle_startendtag(self, tag, attrs):
        if self.in_entry and self.changelog_depth and tag == "br":
            self.changelog_parts.append("\n")

    def handle_endtag(self, tag):
        if self.in_entry:
            if self.version_depth:
                self.version_depth -= 1

            if self.changelog_depth:
                if tag in self.BLOCK_TAGS:
                    self.changelog_parts.append("\n")
                self.changelog_depth -= 1

            if tag == "li":
                self.entry_depth -= 1
                if self.entry_depth == 0:
                    self.entries.append(("".join(self.version_parts), "".join(self.changelog_parts)))
                    self.in_entry = False

        if self.in_history and tag == "ul":
            self.history_ul_depth -= 1
            if self.history_ul_depth == 0:
                self.in_history = False

    def handle_data(self, data):
        if self.in_entry and self.version_depth:
            self.version_parts.append(data)
        if self.in_entry and self.changelog_depth:
            self.changelog_parts.append(data)


def clean_text(value):
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    lines = [line.strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def main():
    if len(sys.argv) != 4:
        raise SystemExit("Usage: extract_greasyfork_changelog.py VERSION HTML_FILE OUTPUT_FILE")

    target_version = sys.argv[1].strip().lstrip("vV")
    html_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    html = html_path.read_text(encoding="utf-8", errors="replace")

    parser = HistoryParser()
    parser.feed(html)

    for raw_version, raw_changelog in parser.entries:
        version_match = re.search(r"(?:^|\s)v?([0-9][0-9A-Za-z._+-]*)", clean_text(raw_version))
        if not version_match:
            continue

        version = version_match.group(1).lstrip("vV")
        if version != target_version:
            continue

        changelog = clean_text(raw_changelog)
        if len(changelog) > 950:
            changelog = changelog[:947].rstrip() + "..."

        output_path.write_text(changelog, encoding="utf-8")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
