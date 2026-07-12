#!/usr/bin/env python3

import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


class HistoryParser(HTMLParser):
    """Extract version/changelog pairs from Greasy Fork's History page reliably."""

    BLOCK_TAGS = {
        "br", "p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
        "section", "article", "blockquote", "pre"
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.history_depth = None
        self.entry_li_depth = 0
        self.version_capture_depth = None
        self.changelog_capture_depth = None
        self.version_parts = []
        self.changelog_parts = []
        self.entries = []

    @staticmethod
    def classes(attrs):
        return set(dict(attrs).get("class", "").split())

    def handle_starttag(self, tag, attrs):
        classes = self.classes(attrs)
        self.stack.append(tag)
        depth = len(self.stack)

        if self.history_depth is None and tag == "ul" and "history_versions" in classes:
            self.history_depth = depth
            return

        if self.history_depth is None:
            return

        if tag == "li":
            if self.entry_li_depth == 0:
                self.entry_li_depth = 1
                self.version_parts = []
                self.changelog_parts = []
            else:
                self.entry_li_depth += 1
                if self.changelog_capture_depth is not None:
                    self.changelog_parts.append("\n• ")

        if self.entry_li_depth:
            if "version-number" in classes and self.version_capture_depth is None:
                self.version_capture_depth = depth

            if "version-changelog" in classes and self.changelog_capture_depth is None:
                self.changelog_capture_depth = depth

            if self.changelog_capture_depth is not None:
                if tag == "br":
                    self.changelog_parts.append("\n")
                elif tag in self.BLOCK_TAGS and depth > self.changelog_capture_depth:
                    self.changelog_parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if self.entry_li_depth and self.changelog_capture_depth is not None and tag == "br":
            self.changelog_parts.append("\n")

    def handle_endtag(self, tag):
        depth = len(self.stack)

        if self.entry_li_depth and self.changelog_capture_depth is not None:
            if tag in self.BLOCK_TAGS and depth > self.changelog_capture_depth:
                self.changelog_parts.append("\n")

        if self.version_capture_depth == depth:
            self.version_capture_depth = None

        if self.changelog_capture_depth == depth:
            self.changelog_capture_depth = None

        if self.history_depth is not None and tag == "li" and self.entry_li_depth:
            self.entry_li_depth -= 1
            if self.entry_li_depth == 0:
                self.entries.append(("".join(self.version_parts), "".join(self.changelog_parts)))

        if self.history_depth == depth and tag == "ul":
            self.history_depth = None

        # Greasy Fork emits well-formed HTML, but recover gracefully if a tag differs.
        if self.stack:
            if self.stack[-1] == tag:
                self.stack.pop()
            elif tag in self.stack:
                reverse_index = self.stack[::-1].index(tag)
                del self.stack[len(self.stack) - reverse_index - 1:]

    def handle_data(self, data):
        if not self.entry_li_depth:
            return
        if self.version_capture_depth is not None:
            self.version_parts.append(data)
        if self.changelog_capture_depth is not None:
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


def regex_fallback(html, target_version):
    """Fallback for minor Greasy Fork markup changes."""
    version_pattern = re.escape(target_version)
    entry_match = re.search(
        rf'<li\b[^>]*>(?:(?!</li>).)*?class=["\'][^"\']*version-number[^"\']*["\'][^>]*>'
        rf'(?:(?!</li>).)*?\bv?{version_pattern}\b(?:(?!</li>).)*?</li>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not entry_match:
        return None

    entry = entry_match.group(0)
    changelog_match = re.search(
        r'class=["\'][^"\']*version-changelog[^"\']*["\'][^>]*>(.*?)</(?:span|div|section)>',
        entry,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not changelog_match:
        return ""

    fragment = changelog_match.group(1)
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"</?(?:p|div|ul|ol|h[1-6]|section|article|blockquote|pre)\b[^>]*>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"<li\b[^>]*>", "\n• ", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"</li>", "", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return clean_text(fragment)


def main():
    if len(sys.argv) != 4:
        raise SystemExit("Usage: extract_greasyfork_changelog.py VERSION HTML_FILE OUTPUT_FILE")

    target_version = sys.argv[1].strip().lstrip("vV")
    html_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    html = html_path.read_text(encoding="utf-8", errors="replace")

    parser = HistoryParser()
    parser.feed(html)

    changelog = None
    for raw_version, raw_changelog in parser.entries:
        if normalise_version(raw_version) == target_version:
            changelog = clean_text(raw_changelog)
            break

    if changelog is None:
        changelog = regex_fallback(html, target_version)

    if changelog is None:
        print(f"Version {target_version} was not found in the Greasy Fork History HTML.", file=sys.stderr)
        return 1

    # Discord embed field values are limited to 1024 characters.
    if len(changelog) > 1000:
        changelog = changelog[:997].rstrip() + "..."

    output_path.write_text(changelog, encoding="utf-8")
    print(f"Matched Greasy Fork version {target_version}; changelog length: {len(changelog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
