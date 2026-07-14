#!/usr/bin/env python3
"""Prepare a rollback candidate from an immutable verified release asset.

The source executable is restored under a new, higher version. This prevents
silent version downgrades and routes the rollback through the ordinary review
and release pipeline.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from datetime import date
from pathlib import Path

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+]([0-9A-Za-z.-]+))?$")
VERSION_LINE_RE = re.compile(r"^(//\s*@version\s+)([^\r\n]+)(\r?)$", re.MULTILINE)


def fail(message: str) -> None:
    raise SystemExit(f"ROLLBACK PREPARATION ERROR: {message}")


def parse_version(value: str) -> tuple[int, int, int, str]:
    match = VERSION_RE.fullmatch(value.strip())
    if not match:
        fail(f"invalid semantic version: {value}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4) or ""


def core(value: str) -> tuple[int, int, int]:
    major, minor, patch, _ = parse_version(value)
    return major, minor, patch


def prepare(
    source_path: Path,
    output_path: Path,
    changelog_path: Path,
    source_version: str,
    recovery_version: str,
    current_version: str,
) -> dict[str, str]:
    parse_version(source_version)
    parse_version(recovery_version)
    parse_version(current_version)

    if core(recovery_version) <= core(current_version):
        fail(
            f"recovery version {recovery_version} must be higher than current version {current_version}"
        )
    if recovery_version == source_version:
        fail("recovery version must differ from the restored source version")

    raw = source_path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"source release asset is not valid UTF-8: {exc}")

    matches = list(VERSION_LINE_RE.finditer(text))
    if len(matches) != 1:
        fail("source release asset must contain exactly one @version line")
    observed = matches[0].group(2).strip()
    if observed != source_version:
        fail(f"source release asset reports @version {observed}, expected {source_version}")

    replacement = f"{matches[0].group(1)}{recovery_version}{matches[0].group(3)}"
    candidate = text[: matches[0].start()] + replacement + text[matches[0].end() :]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(candidate, encoding="utf-8", newline="")

    changelog = changelog_path.read_text(encoding="utf-8")
    heading_pattern = re.compile(rf"^## \[{re.escape(recovery_version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$", re.M)
    if heading_pattern.search(changelog):
        fail(f"CHANGELOG.md already contains version {recovery_version}")

    section = (
        f"## [{recovery_version}] - {date.today().isoformat()}\n\n"
        "### Emergency recovery\n\n"
        f"- Restores the last verified executable implementation from Toolkit v{source_version}.\n"
        f"- Publishes the restored implementation as v{recovery_version} so users receive a monotonic update rather than a silent downgrade.\n"
        "- Contains no intentional feature additions beyond recovery metadata and release records.\n\n"
    )

    first_heading = re.search(r"^# .+$", changelog, re.M)
    if first_heading:
        insertion = first_heading.end()
        prefix = changelog[:insertion].rstrip() + "\n\n"
        suffix = changelog[insertion:].lstrip("\r\n")
        changelog_path.write_text(prefix + section + suffix, encoding="utf-8")
    else:
        changelog_path.write_text(section + changelog, encoding="utf-8")

    return {
        "sourceVersion": source_version,
        "recoveryVersion": recovery_version,
        "currentVersion": current_version,
        "output": str(output_path),
        "changelog": str(changelog_path),
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source.user.js"
        output = root / "candidate.user.js"
        changelog = root / "CHANGELOG.md"
        source.write_text(
            "// ==UserScript==\n// @name Test\n// @version 1.2.3\n// ==/UserScript==\nconsole.log('stable');\n",
            encoding="utf-8",
        )
        changelog.write_text("# Changelog\n\n## [1.2.3]\n\n- Stable.\n", encoding="utf-8")
        result = prepare(source, output, changelog, "1.2.3", "1.2.5", "1.2.4")
        assert "@version 1.2.5" in output.read_text(encoding="utf-8")
        assert "console.log('stable')" in output.read_text(encoding="utf-8")
        assert "## [1.2.5]" in changelog.read_text(encoding="utf-8")
        assert result["recoveryVersion"] == "1.2.5"

        try:
            prepare(source, output, changelog, "1.2.3", "1.2.4", "1.2.4")
        except SystemExit:
            pass
        else:
            raise AssertionError("non-monotonic recovery version was accepted")

    print("Rollback candidate self-tests passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source")
    parser.add_argument("--output")
    parser.add_argument("--changelog")
    parser.add_argument("--source-version")
    parser.add_argument("--recovery-version")
    parser.add_argument("--current-version")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    required = {
        "--source": args.source,
        "--output": args.output,
        "--changelog": args.changelog,
        "--source-version": args.source_version,
        "--recovery-version": args.recovery_version,
        "--current-version": args.current_version,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        fail("missing arguments: " + ", ".join(missing))

    result = prepare(
        Path(args.source),
        Path(args.output),
        Path(args.changelog),
        args.source_version,
        args.recovery_version,
        args.current_version,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
