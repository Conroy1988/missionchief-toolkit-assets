#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SECTION_ICONS = {
    "performance": "⚡",
    "added": "✨",
    "changed": "🔧",
    "fixed": "🛠️",
    "security": "🛡️",
    "distribution": "📡",
    "baseline": "🧱",
    "removed": "🗑️",
}

SECTION_PRIORITY = {
    "security": 0,
    "fixed": 1,
    "added": 2,
    "changed": 3,
    "performance": 4,
    "removed": 5,
    "distribution": 6,
    "baseline": 7,
}

MAX_SECTIONS = 2
MAX_ITEMS = 4
MAX_ITEM_LENGTH = 165
MAX_BRIEF_LENGTH = 760


def clean_text(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[*_~]+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def shorten(value: str, limit: int) -> str:
    value = clean_text(value)
    if len(value) <= limit:
        return value
    return value[: max(1, limit - 1)].rstrip(" ,;:-") + "…"


def parse_changelog(path: Path) -> str:
    sections: list[tuple[str, list[str], int]] = []
    current_name = "Release"
    current_items: list[str] = []
    source_order = 0

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# ") or line.startswith("## "):
            continue

        heading = re.match(r"^#{3,6}\s+(.+?)\s*$", line)
        if heading:
            if current_items:
                sections.append((current_name, current_items, source_order))
                source_order += 1
            current_name = clean_text(heading.group(1)) or "Release"
            current_items = []
            continue

        bullet = re.match(r"^(?:[-*•]|(?:\d+\.))\s+(.+?)\s*$", line)
        if bullet:
            current_items.append(shorten(bullet.group(1), MAX_ITEM_LENGTH))
            continue

        if current_items:
            current_items[-1] = shorten(
                f"{current_items[-1]} {line}",
                MAX_ITEM_LENGTH,
            )

    if current_items:
        sections.append((current_name, current_items, source_order))

    if not sections:
        fallback = shorten(path.read_text(encoding="utf-8"), 520)
        return fallback or "Open the release notes for the complete change list."

    total_items = sum(len(items) for _, items, _ in sections)
    ranked = sorted(
        sections,
        key=lambda entry: (
            SECTION_PRIORITY.get(entry[0].casefold(), 99),
            entry[2],
        ),
    )

    rendered: list[str] = []
    used_items = 0
    used_sections = 0

    for name, items, _ in ranked:
        if used_sections >= MAX_SECTIONS or used_items >= MAX_ITEMS:
            break

        available = MAX_ITEMS - used_items
        selected_items = items[:available]
        if not selected_items:
            continue

        icon = SECTION_ICONS.get(name.casefold(), "◆")
        rendered.append(f"**{icon} {name.title()}**")
        rendered.extend(f"• {item}" for item in selected_items)
        used_items += len(selected_items)
        used_sections += 1

    omitted = max(0, total_items - used_items)
    if omitted:
        suffix = "s" if omitted != 1 else ""
        rendered.append(f"*{omitted} more change{suffix} in the full release notes.*")

    brief = "\n".join(rendered)
    if len(brief) > MAX_BRIEF_LENGTH:
        brief = brief[: MAX_BRIEF_LENGTH - 1].rstrip() + "…"
    return brief


def short_hash(value: str, head: int = 8, tail: int = 6) -> str:
    value = value.strip()
    if len(value) <= head + tail + 1:
        return value
    return f"{value[:head]}…{value[-tail:]}"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def build_primary(args: argparse.Namespace, brief: str) -> dict:
    integrity = (
        f"SHA-256 `{short_hash(args.sha256)}`\n"
        f"Backup `{args.backup_commit[:10]}`"
    )

    return {
        "username": "MissionChief Toolkit Releases",
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "author": {
                    "name": "MissionChief Map Command Toolkit",
                    "url": args.release_url,
                },
                "title": f"✅ Toolkit v{args.version} is live",
                "description": (
                    "The verified update is available now on Greasy Fork.\n"
                    "**Update to receive the latest fixes and improvements.**"
                ),
                "url": args.release_url,
                "color": 0x2ECC71,
                "fields": [
                    {
                        "name": "Release",
                        "value": (
                            f"**v{args.version}**\n"
                            f"[Public release]({args.release_url})"
                        ),
                        "inline": True,
                    },
                    {
                        "name": "Availability",
                        "value": "Greasy Fork ✅\nInstall source ✅",
                        "inline": True,
                    },
                    {
                        "name": "Verification",
                        "value": "GitHub ✅\nPrivate backup ✅",
                        "inline": True,
                    },
                    {
                        "name": "What changed",
                        "value": brief,
                        "inline": False,
                    },
                    {
                        "name": "Release integrity",
                        "value": integrity,
                        "inline": False,
                    },
                    {
                        "name": "Update now",
                        "value": (
                            f"**[⬇️ Install / Update]({args.install_url})**"
                            f"  •  [Release notes]({args.release_url})"
                            f"  •  [Greasy Fork page]({args.script_url})"
                        ),
                        "inline": False,
                    },
                ],
                "footer": {
                    "text": "Verified deployment • MissionChief Toolkit",
                },
                "timestamp": utc_timestamp(),
            }
        ],
    }


def build_fallback(args: argparse.Namespace, brief: str) -> dict:
    history_url = args.history_url or f"{args.script_url.rstrip('/')}/versions"
    previous = args.previous_version or "unknown"
    previous_label = f"v{previous}" if previous != "unknown" else "Unknown"

    return {
        "username": "MissionChief Toolkit Releases",
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "author": {
                    "name": "MissionChief Map Command Toolkit",
                    "url": args.script_url,
                },
                "title": f"📡 Toolkit v{args.version} detected on Greasy Fork",
                "description": (
                    "The public version changed before the standard release "
                    "announcement completed. The update is available now."
                ),
                "url": args.script_url,
                "color": 0xF39C12,
                "fields": [
                    {
                        "name": "Version change",
                        "value": f"`{previous_label}` → **v{args.version}**",
                        "inline": True,
                    },
                    {
                        "name": "Source",
                        "value": "Greasy Fork ✅",
                        "inline": True,
                    },
                    {
                        "name": "Status",
                        "value": "Fallback notice",
                        "inline": True,
                    },
                    {
                        "name": "What changed",
                        "value": brief,
                        "inline": False,
                    },
                    {
                        "name": "Update now",
                        "value": (
                            f"**[⬇️ Install / Update]({args.install_url})**"
                            f"  •  [Version history]({history_url})"
                            f"  •  [Greasy Fork page]({args.script_url})"
                        ),
                        "inline": False,
                    },
                ],
                "footer": {
                    "text": "Fallback release signal • MissionChief Toolkit",
                },
                "timestamp": utc_timestamp(),
            }
        ],
    }


def validate_payload(payload: dict) -> None:
    encoded = json.dumps(payload, ensure_ascii=False)
    if len(encoded.encode("utf-8")) > 20_000:
        raise SystemExit("Discord payload is unexpectedly large.")

    embeds = payload.get("embeds", [])
    if len(embeds) != 1:
        raise SystemExit("Expected exactly one Discord embed.")

    embed = embeds[0]
    if len(embed.get("title", "")) > 256:
        raise SystemExit("Discord embed title exceeds 256 characters.")
    if len(embed.get("description", "")) > 4096:
        raise SystemExit("Discord embed description exceeds 4096 characters.")
    if len(embed.get("fields", [])) > 25:
        raise SystemExit("Discord embed contains more than 25 fields.")

    total_characters = (
        len(embed.get("title", ""))
        + len(embed.get("description", ""))
        + len(embed.get("author", {}).get("name", ""))
        + len(embed.get("footer", {}).get("text", ""))
    )

    for field in embed.get("fields", []):
        name = field.get("name", "")
        value = field.get("value", "")
        if len(name) > 256 or len(value) > 1024:
            raise SystemExit(f"Discord embed field exceeds limits: {name}")
        total_characters += len(name) + len(value)

    if total_characters > 6000:
        raise SystemExit("Discord embed exceeds the 6000-character total limit.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a styled Discord Toolkit release embed.",
    )
    parser.add_argument(
        "--mode",
        choices=("primary", "fallback"),
        required=True,
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--changelog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--release-url", default="")
    parser.add_argument("--script-url", required=True)
    parser.add_argument("--install-url", required=True)
    parser.add_argument("--history-url", default="")
    parser.add_argument("--previous-version", default="")
    parser.add_argument("--sha256", default="")
    parser.add_argument("--backup-commit", default="")
    args = parser.parse_args()

    if not args.changelog.is_file():
        raise SystemExit(f"Changelog file not found: {args.changelog}")

    if args.mode == "primary":
        missing = [
            name
            for name, value in (
                ("release URL", args.release_url),
                ("SHA-256", args.sha256),
                ("backup commit", args.backup_commit),
            )
            if not value
        ]
        if missing:
            raise SystemExit(
                "Missing primary release values: " + ", ".join(missing),
            )

    brief = parse_changelog(args.changelog)
    if args.mode == "primary":
        payload = build_primary(args, brief)
    else:
        payload = build_fallback(args, brief)

    validate_payload(payload)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Built {args.mode} Discord release payload: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
