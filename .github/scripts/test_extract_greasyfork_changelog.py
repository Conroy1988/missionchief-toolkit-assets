#!/usr/bin/env python3

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXTRACTOR = ROOT / "extract_greasyfork_changelog.py"


def run_case(version: str, html: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        html_path = temp / "history.html"
        output_path = temp / "changelog.txt"
        html_path.write_text(html, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(EXTRACTOR), version, str(html_path), str(output_path)],
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
    # The void <input> elements match Greasy Fork's real History markup and must
    # not corrupt the parser's element depth.
    result, output = run_case(
        "3.5.1",
        history(
            entry(
                "3.5.1",
                "<p>Major update</p><ul><li>New mobile controls</li><li>Performance fixes</li></ul>",
            )
            + entry("3.4.2", "<p>Older changelog</p>")
        ),
    )
    assert result.returncode == 0, result.stderr
    assert output is not None
    assert "Major update" in output
    assert "New mobile controls" in output
    assert "Performance fixes" in output

    # A new version without a changelog must produce an empty result rather
    # than incorrectly repeating the previous version's changelog.
    result, output = run_case(
        "3.5.2",
        history(entry("3.5.2", None) + entry("3.5.1", "<p>Do not repeat this</p>")),
    )
    assert result.returncode == 0, result.stderr
    assert output == ""

    # If the page has not refreshed to the requested version yet, fail so the
    # workflow retries later instead of posting a changelog from an old entry.
    result, output = run_case(
        "3.5.3",
        history(entry("3.5.2", "<p>Old information</p>")),
    )
    assert result.returncode != 0
    assert output is None

    print("Greasy Fork changelog extractor tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
