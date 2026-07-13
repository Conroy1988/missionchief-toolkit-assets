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

VERSION_LINE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:[○●◯◉◌]\s*)*"
    r"v?([0-9]+(?:\.[0-9A-Za-z_-]+)+)"
    r"(?:\s*(?:[-–—:|]\s*)?)(.*)$",
    re.IGNORECASE,
)

RELATIVE_TIME = re.compile(
    r"^(?:"
    r"just\s+now|now|today(?:\s+at\s+\d{1,2}:\d{2})?|"
    r"\d+\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago|"
    r"\d{4}-\d{2}-\d{2}(?:[T\s]\d{1,2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)?"
    r")\b[\s:–—-]*",
    re.IGNORECASE,
)

BOILERPLATE_LINES = {
    "diff selected versions",
    "show all versions",
    "show only versions where the code was updated",
    "these are versions of this script where the code was updated.",
    "these are all versions of this script.",
}

DISCORD_FIELD_LIMIT = 1000


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
    match = re.search(r"(?:^|\s)v?([0-9]+(?:\.[0-9A-Za-z_-]+)+)", clean_text(value))
    return match.group(1).lstrip("vV") if match else None


def clean_reader_fragment(value):
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("`", "")
    value = clean_text(value)

    cleaned_lines = []
    for line in value.splitlines():
        line = re.sub(r"^[○●◯◉◌\s]+", "", line).strip()
        line = RELATIVE_TIME.sub("", line).strip()
        line = re.sub(
            r"^(?:ago|at\s+\d{1,2}:\d{2})\b[\s:–—-]*",
            "",
            line,
            flags=re.IGNORECASE,
        ).strip()
        if not line:
            continue
        if line.casefold() in BOILERPLATE_LINES:
            continue
        if line.startswith(("http://", "https://")):
            continue
        cleaned_lines.append(line)

    return clean_text("\n".join(cleaned_lines))


def parse_reader_entries(text):
    """Parse reader/Markdown/plain-text output as a fallback."""
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    lines = text.splitlines()

    entries = []
    current_version = None
    current_parts = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if current_version is not None:
                current_parts.append("")
            continue

        match = VERSION_LINE.match(line)
        if match:
            if current_version is not None:
                entries.append(
                    (current_version, clean_reader_fragment("\n".join(current_parts)))
                )

            current_version = match.group(1).lstrip("vV")
            remainder = clean_reader_fragment(match.group(2))
            current_parts = [remainder] if remainder else []
            continue

        if current_version is not None:
            current_parts.append(line)

    if current_version is not None:
        entries.append((current_version, clean_reader_fragment("\n".join(current_parts))))

    deduplicated = []
    for entry in entries:
        if not deduplicated or entry != deduplicated[-1]:
            deduplicated.append(entry)
    return deduplicated


def extract_entries(document):
    parser = HistoryParser()
    parser.feed(document)

    html_entries = []
    for raw_version, raw_changelog in parser.entries:
        version = normalise_version(raw_version)
        if version:
            html_entries.append((version, clean_text(raw_changelog)))

    if html_entries:
        return html_entries, "Greasy Fork HTML"

    return parse_reader_entries(document), "reader text"


def format_changelogs(newest_first):
    """Fit changelog sections into Discord while always preserving newest notes."""
    chronological = list(reversed(newest_first))
    sections = [f"**v{version}**\n{changelog}" for version, changelog in chronological]
    combined = "\n\n".join(sections)

    if len(combined) <= DISCORD_FIELD_LIMIT:
        return combined

    # Drop the oldest sections first. The previous implementation cut the end of
    # the string, which removed the newest release notes and repeated old entries.
    for omitted in range(1, len(sections)):
        label = "entry" if omitted == 1 else "entries"
        note = (
            f"_Omitted {omitted} earlier unannounced changelog {label}; "
            "see version history._"
        )
        candidate = note + "\n\n" + "\n\n".join(sections[omitted:])
        if len(candidate) <= DISCORD_FIELD_LIMIT:
            return candidate

    # The newest single changelog is itself too long. Keep its beginning and state
    # clearly that it was shortened, rather than losing the newest release entirely.
    latest = sections[-1]
    if len(sections) > 1:
        note = (
            f"_Omitted {len(sections) - 1} earlier unannounced changelog "
            f"{'entry' if len(sections) == 2 else 'entries'}; "
            "the latest entry was shortened. See version history._\n\n"
        )
    else:
        note = "_The latest changelog was shortened; see version history._\n\n"

    available = max(0, DISCORD_FIELD_LIMIT - len(note) - 3)
    return note + latest[:available].rstrip() + "..."


def main():
    if len(sys.argv) != 5:
        raise SystemExit(
            "Usage: extract_greasyfork_changelog.py CURRENT_VERSION "
            "PREVIOUS_VERSION SOURCE_FILE OUTPUT_FILE"
        )

    current_version = sys.argv[1].strip().lstrip("vV")
    previous_version = sys.argv[2].strip().lstrip("vV")
    source_path = Path(sys.argv[3])
    output_path = Path(sys.argv[4])
    document = source_path.read_text(encoding="utf-8", errors="replace")

    entries, source_kind = extract_entries(document)

    if not entries:
        print("No Greasy Fork version entries were found.", file=sys.stderr)
        return 1

    latest_version = entries[0][0]
    if latest_version != current_version:
        print(
            f"Latest {source_kind} version is {latest_version}, expected {current_version}.",
            file=sys.stderr,
        )
        return 1

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
            f"Previously announced version {previous_version} was not found in {source_kind}.",
            file=sys.stderr,
        )
        return 1

    combined = format_changelogs(new_changelogs)

    output_path.write_text(combined, encoding="utf-8")
    print(
        f"Matched {source_kind} range {previous_version or 'initial'} -> {current_version}; "
        f"new changelog entries: {len(new_changelogs)}; output length: {len(combined)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
