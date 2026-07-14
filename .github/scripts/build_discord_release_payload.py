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

MAX_SECTIONS = 3
MAX_ITEMS = 6
MAX_ITEM_LENGTH = 220
MAX_BRIEF_LENGTH = 1000


def clean_text(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_~]+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def shorten(value: str, limit: int) -> str:
    value = clean_text(value)
    if len(value) <= limit:
        return value
    return value[: max(1, limit - 1)].rstrip(" ,;:-") + "…"


def parse_changelog(path: Path) -> str:
    sections: list[tuple[str, list[str]]] = []
    current_name = "Release"
    current_items: list[str] = []
    total_items = 0

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# ") or line.startswith("## "):
            continue

        heading = re.match(r"^#{3,6}\s+(.+?)\s*$", line)
        if heading:
            if current_items:
                sections.append((current_name, current_items))
            current_name = clean_text(heading.group(1)) or "Release"
            current_items = []
            continue

        bullet = re.match(r"^(?:[-*•]|(?:\d+\.))\s+(.+?)\s*$", line)
        if bullet:
            total_items += 1
            current_items.append(shorten(bullet.group(1), MAX_ITEM_LENGTH))
            continue

        if current_items:
            current_items[-1] = shorten(f"{current_items[-1]} {line}", MAX_ITEM_LENGTH)

    if current_items:
        sections.append((current_name, current_items))

    if not sections:
        fallback = shorten(path.read_text(encoding="utf-8"), 800)
        return fallback or "Release notes are available from the linked release page."

    rendered: list[str] = []
    used_items = 0
    for name, items in sections[:MAX_SECTIONS]:
        if used_items >= MAX_ITEMS:
            break
        icon = SECTION_ICONS.get(name.casefold(), "◆")
        rendered.append(f"**{icon} {name.upper()}**")
        for item in items:
            if used_items >= MAX_ITEMS:
                break
            rendered.append(f"▸ {item}")
            used_items += 1

    omitted = max(0, total_items - used_items)
    if omitted:
        suffix = "s" if omitted != 1 else ""
        rendered.append(f"*+ {omitted} additional change{suffix} in the full release notes.*")

    brief = "\n".join(rendered)
    if len(brief) > MAX_BRIEF_LENGTH:
        brief = brief[: MAX_BRIEF_LENGTH - 1].rstrip() + "…"
    return brief


def short_hash(value: str) -> str:
    value = value.strip()
    if len(value) <= 20:
        return value
    return f"{value[:10]}…{value[-8:]}"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_primary(args: argparse.Namespace, brief: str) -> dict:
    return {
        "username": "MissionChief Toolkit Releases",
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "author": {"name": "MISSION CONTROL // RELEASE OPERATIONS"},
            "title": f"🚨 TOOLKIT DEPLOYMENT COMPLETE // v{args.version}",
            "description": (
                "**STATUS: LIVE**\n"
                "The latest command package has cleared every release gate and is now active on Greasy Fork."
            ),
            "url": args.release_url,
            "color": 0x00AEEF,
            "fields": [
                {
                    "name": "🚀 DEPLOYMENT",
                    "value": f"**v{args.version}**\nPublic release live",
                    "inline": True,
                },
                {
                    "name": "🛡️ VERIFICATION",
                    "value": "GitHub ✅\nGreasy Fork ✅",
                    "inline": True,
                },
                {
                    "name": "💾 RECOVERY",
                    "value": f"Private archive ✅\n`{args.backup_commit[:10]}`",
                    "inline": True,
                },
                {
                    "name": "⚙️ MISSION BRIEF",
                    "value": brief,
                    "inline": False,
                },
                {
                    "name": "🔐 BUILD SIGNATURE",
                    "value": f"`{short_hash(args.sha256)}`",
                    "inline": False,
                },
                {
                    "name": "🔗 COMMAND LINKS",
                    "value": (
                        f"[⬇️ Install / Update]({args.install_url})"
                        f"  •  [📋 Full Release]({args.release_url})"
                        f"  •  [🛠️ Greasy Fork]({args.script_url})"
                    ),
                    "inline": False,
                },
            ],
            "footer": {"text": "MISSIONCHIEF MAP COMMAND TOOLKIT • VERIFIED DEPLOYMENT"},
            "timestamp": utc_timestamp(),
        }],
    }


def build_fallback(args: argparse.Namespace, brief: str) -> dict:
    history_url = args.history_url or f"{args.script_url.rstrip('/')}/versions"
    previous = args.previous_version or "unknown"
    previous_label = f"v{previous}" if previous != "unknown" else "Unknown"
    return {
        "username": "MissionChief Toolkit Releases",
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "author": {"name": "MISSION CONTROL // RELEASE SIGNAL"},
            "title": f"📡 TOOLKIT RELEASE SIGNAL ACQUIRED // v{args.version}",
            "description": (
                "**STATUS: LIVE ON GREASY FORK**\n"
                "The fallback monitor detected a public version that had not yet been announced."
            ),
            "url": args.script_url,
            "color": 0xF0A500,
            "fields": [
                {
                    "name": "⏮️ PREVIOUS",
                    "value": f"`{previous_label}`",
                    "inline": True,
                },
                {
                    "name": "🚀 NOW LIVE",
                    "value": f"**v{args.version}**",
                    "inline": True,
                },
                {
                    "name": "📡 SOURCE",
                    "value": "Greasy Fork ✅",
                    "inline": True,
                },
                {
                    "name": "⚙️ MISSION BRIEF",
                    "value": brief,
                    "inline": False,
                },
                {
                    "name": "🔗 COMMAND LINKS",
                    "value": (
                        f"[⬇️ Install / Update]({args.install_url})"
                        f"  •  [📜 Version History]({history_url})"
                        f"  •  [🛠️ Greasy Fork]({args.script_url})"
                    ),
                    "inline": False,
                },
            ],
            "footer": {"text": "MISSIONCHIEF MAP COMMAND TOOLKIT • FALLBACK RELEASE SIGNAL"},
            "timestamp": utc_timestamp(),
        }],
    }


def validate_payload(payload: dict) -> None:
    encoded = json.dumps(payload, ensure_ascii=False)
    if len(encoded.encode("utf-8")) > 20_000:
        raise SystemExit("Discord payload is unexpectedly large.")

    embed = payload["embeds"][0]
    if len(embed.get("title", "")) > 256:
        raise SystemExit("Discord embed title exceeds 256 characters.")

    for field in embed.get("fields", []):
        if len(field["name"]) > 256 or len(field["value"]) > 1024:
            raise SystemExit(f"Discord embed field exceeds limits: {field['name']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a styled Discord Toolkit release embed.")
    parser.add_argument("--mode", choices=("primary", "fallback"), required=True)
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
            name for name, value in (
                ("release URL", args.release_url),
                ("SHA-256", args.sha256),
                ("backup commit", args.backup_commit),
            ) if not value
        ]
        if missing:
            raise SystemExit("Missing primary release values: " + ", ".join(missing))

    brief = parse_changelog(args.changelog)
    payload = build_primary(args, brief) if args.mode == "primary" else build_fallback(args, brief)
    validate_payload(payload)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built {args.mode} Discord release payload: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
