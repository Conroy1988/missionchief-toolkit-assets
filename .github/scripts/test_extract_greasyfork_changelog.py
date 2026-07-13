#!/usr/bin/env python3

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXTRACTOR = ROOT / "extract_greasyfork_changelog.py"


def run_case(current: str, previous: str, source: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        source_path = temp / "history-source.txt"
        output_path = temp / "changelog.txt"
        source_path.write_text(source, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                str(EXTRACTOR),
                current,
                previous,
                str(source_path),
                str(output_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

        output = output_path.read_text(encoding="utf-8") if output_path.exists() else None
        return result, output


def history(entries: str) -> str:
    return f"""
    <!doctype html>
    <html>
      <body>
        <form>
          <ul class="history_versions">
            {entries}
          </ul>
        </form>
      </body>
    </html>
    """


def entry(version: str, changelog: str | None) -> str:
    changelog_html = "" if changelog is None else f'<span class="version-changelog">{changelog}</span>'
    return f"""
    <li>
      <span class="diff-controls">
        <input type="radio" name="v1" value="123" checked>
        <input type="radio" name="v2" value="122">
      </span>
      <span class="version-number"><a href="#">v{version}</a></span>
      <relative-time datetime="2026-07-12T20:00:00Z">now</relative-time>
      {changelog_html}
    </li>
    """


def main() -> int:
    # Several releases happened before the workflow ran. The latest version has
    # no changelog, but an intermediate version does. Include it only once.
    result, output = run_case(
        "3.7.1",
        "3.5.1",
        history(
            entry("3.7.1", None)
            + entry("3.7.0", None)
            + entry("3.6.0", "<p>Major interface update</p>")
            + entry("3.5.1", "<p>Already announced</p>")
        ),
    )
    assert result.returncode == 0, result.stderr
    assert output is not None
    assert "**v3.6.0**" in output
    assert "Major interface update" in output
    assert "Already announced" not in output

    # Multiple short changelogs remain chronological.
    result, output = run_case(
        "4.0.0",
        "3.7.1",
        history(
            entry("4.0.0", "<p>Current release</p>")
            + entry("3.9.0", "<p>Earlier release</p>")
            + entry("3.7.1", "<p>Do not repeat</p>")
        ),
    )
    assert result.returncode == 0, result.stderr
    assert output is not None
    assert output.index("**v3.9.0**") < output.index("**v4.0.0**")
    assert "Do not repeat" not in output

    # When the Discord limit is exceeded, older sections are omitted first and
    # the newest release notes are always retained.
    result, output = run_case(
        "5.0.0",
        "4.7.0",
        history(
            entry("5.0.0", "<p>LATEST UNIQUE RELEASE NOTES</p>")
            + entry("4.9.0", "<p>" + ("Middle changes " * 55) + "</p>")
            + entry("4.8.0", "<p>" + ("Old changes " * 65) + "</p>")
            + entry("4.7.0", "<p>Already announced</p>")
        ),
    )
    assert result.returncode == 0, result.stderr
    assert output is not None
    assert len(output) <= 1000
    assert "LATEST UNIQUE RELEASE NOTES" in output
    assert "Omitted" in output
    assert "Already announced" not in output

    # A single oversized latest changelog is shortened rather than discarded.
    result, output = run_case(
        "5.1.0",
        "5.0.0",
        history(
            entry("5.1.0", "<p>LATEST START " + ("detail " * 300) + "</p>")
            + entry("5.0.0", "<p>Already announced</p>")
        ),
    )
    assert result.returncode == 0, result.stderr
    assert output is not None
    assert len(output) <= 1000
    assert "LATEST START" in output
    assert "shortened" in output

    # New versions without any changelog produce an empty result, not an old one.
    result, output = run_case(
        "4.0.2",
        "4.0.0",
        history(
            entry("4.0.2", None)
            + entry("4.0.1", None)
            + entry("4.0.0", "<p>Do not repeat this</p>")
        ),
    )
    assert result.returncode == 0, result.stderr
    assert output == ""

    # If the page has not refreshed to the requested current version, fail so
    # the workflow retries rather than posting against stale History data.
    result, output = run_case(
        "4.1.0",
        "4.0.2",
        history(entry("4.0.2", "<p>Old information</p>")),
    )
    assert result.returncode != 0
    assert output is None

    # The previous announcement boundary must be present.
    result, output = run_case(
        "4.2.0",
        "3.0.0",
        history(entry("4.2.0", "<p>New</p>") + entry("4.1.0", "<p>Other</p>")),
    )
    assert result.returncode != 0
    assert output is None

    # Reader-style Markdown works when Greasy Fork blocks GitHub Actions.
    reader_markdown = """
Title: Version history for MissionChief Map Command Toolkit
URL Source: https://greasyfork.org/en/scripts/586018/versions
Markdown Content:
These are versions of this script where the code was updated. Show all versions.

○ ○ [v4.4.0](https://greasyfork.org/en/scripts/586018?version=144) 2 minutes ago Major mobile update
- Added responsive controls
- Fixed the tablet layout

○ ○ [v4.3.0](https://greasyfork.org/en/scripts/586018?version=143) 1 hour ago

○ ○ [v4.2.0](https://greasyfork.org/en/scripts/586018?version=142) 2 hours ago Already announced
"""
    result, output = run_case("4.4.0", "4.2.0", reader_markdown)
    assert result.returncode == 0, result.stderr
    assert output is not None
    assert "**v4.4.0**" in output
    assert "Major mobile update" in output
    assert "Added responsive controls" in output
    assert "Already announced" not in output

    print("Greasy Fork changelog extractor tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
