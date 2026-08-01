#!/usr/bin/env python3
"""Build the first-party TKB Website Toolkit distribution assets."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST = ROOT / "dist"
INSTALL = DIST / "MissionChief_Map_Command_Toolkit.install.user.js"
UPDATE = DIST / "MissionChief_Map_Command_Toolkit.update.user.js"
METADATA = DIST / "MissionChief_Map_Command_Toolkit.meta.js"
STYLESHEET = DIST / "MissionChief_Map_Command_Toolkit.css"


class DistributionError(RuntimeError):
    """Fail-closed distribution build error."""


@dataclass(frozen=True)
class VariantResult:
    version: str
    stylesheet_sha256: str
    stylesheet_bytes: int


def fail(message: str) -> None:
    raise DistributionError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def metadata_block(source: str) -> str:
    marker = "// ==/UserScript=="
    end = source.find(marker)
    if end < 0:
        fail("userscript metadata block is missing")
    return source[: end + len(marker)] + "\n"


def version_of(source: str) -> str:
    matches = re.findall(r"^//\s*@version\s+(\S+)\s*$", source, re.MULTILINE)
    if len(matches) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", matches[0]):
        fail("one stable semantic @version is required")
    return matches[0]


def static_object_values(source: str, object_name: str) -> dict[str, str]:
    patterns = [
        rf"const\s+{re.escape(object_name)}\s*=\s*\{{(.*?)\n\s*\}};",
        rf"const\s+{re.escape(object_name)}\s*=\s*Object\.freeze\(\{{(.*?)\n\s*\}}\);",
    ]
    body = None
    for pattern in patterns:
        match = re.search(pattern, source, re.DOTALL)
        if match:
            body = match.group(1)
            break
    if body is None:
        fail(f"static object {object_name} was not found")
    values = {
        key: value
        for key, value in re.findall(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*'([^']*)'\s*,?\s*$", body, re.MULTILINE)
    }
    if not values:
        fail(f"static object {object_name} has no supported string values")
    return values


def main_styles_template(source: str) -> tuple[int, int, str]:
    function_start = source.find("    function installMainStyles()")
    if function_start < 0:
        fail("installMainStyles was not found")
    call_start = source.find("        addStyle(`", function_start)
    if call_start < 0:
        fail("installMainStyles no longer contains the canonical template")
    content_start = call_start + len("        addStyle(`")
    call_end = source.find("`);", content_start)
    metric = source.find("recordStartupMetric('stylesheetInstallMs'", content_start)
    if call_end < 0 or metric < 0 or call_end > metric:
        fail("installMainStyles template boundary is malformed")
    return call_start, call_end + len("`);"), source[content_start:call_end]


def render_stylesheet(source: str) -> str:
    _, _, template = main_styles_template(source)
    namespaces = {
        "SCRIPT": static_object_values(source, "SCRIPT"),
        "THEME_ASSETS": static_object_values(source, "THEME_ASSETS"),
    }

    unresolved: list[str] = []

    def substitute(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        parts = expression.split(".")
        if len(parts) != 2 or parts[0] not in namespaces or parts[1] not in namespaces[parts[0]]:
            unresolved.append(expression)
            return match.group(0)
        return namespaces[parts[0]][parts[1]]

    rendered = re.sub(r"\$\{([^}]+)\}", substitute, template)
    if unresolved or "${" in rendered:
        fail("unsupported stylesheet interpolation: " + ", ".join(sorted(set(unresolved))))
    if len(rendered.encode("utf-8")) < 500_000:
        fail("rendered main stylesheet is unexpectedly small")
    return rendered


def build() -> VariantResult:
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode("utf-8")
    version = version_of(source)
    DIST.mkdir(parents=True, exist_ok=True)

    INSTALL.write_bytes(source_bytes)
    UPDATE.write_bytes(source_bytes)
    METADATA.write_text(metadata_block(source), encoding="utf-8")

    stylesheet = render_stylesheet(source)
    stylesheet_bytes = stylesheet.encode("utf-8")
    STYLESHEET.write_bytes(stylesheet_bytes)
    stylesheet_hash = sha256_bytes(stylesheet_bytes)

    return VariantResult(
        version=version,
        stylesheet_sha256=stylesheet_hash,
        stylesheet_bytes=len(stylesheet_bytes),
    )


def main() -> int:
    result = build()
    print(json.dumps({
        "version": result.version,
        "stylesheetSha256": result.stylesheet_sha256,
        "stylesheetBytes": result.stylesheet_bytes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DistributionError as error:
        raise SystemExit(f"DISTRIBUTION ERROR: {error}") from error
