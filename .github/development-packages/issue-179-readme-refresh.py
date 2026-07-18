#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


text = README.read_text(encoding="utf-8")

text = replace_once(
    text,
    "Mission intelligence · Fleet awareness · Geographic coverage · Financial command · Responsive layouts · Seven complete interface systems",
    "Mission intelligence · Specialist fleet identity · Geographic coverage · Financial command · Responsive layouts · Seven complete interface systems",
    "hero capability line",
)

text = replace_once(
    text,
    "[Why it exists](#why-it-exists) · [Install](#install-in-under-a-minute) · [Systems](#operational-systems) · [Themes](#seven-interface-systems) · [Devices](#built-for-every-screen) · [Release confidence](#release-confidence) · [Support](#support-and-development)",
    "[Why it exists](#why-it-exists) · [Install](#install-in-under-a-minute) · [Specialist fleet](#specialist-fleet-intelligence) · [Systems](#operational-systems) · [Themes](#seven-interface-systems) · [Devices](#built-for-every-screen) · [Release confidence](#release-confidence) · [Support](#support-and-development)",
    "README navigation",
)

text = replace_once(
    text,
    "**MissionChief Map Command Toolkit brings those signals back into one command layer.** It helps you identify what needs attention, understand the state of your fleet, assess coverage, track mission value and move between incidents without losing the map.",
    "**MissionChief Map Command Toolkit brings those signals back into one command layer.** It helps you identify what needs attention, understand the state and operational identity of your fleet, assess coverage, track mission value and move between incidents without losing the map.",
    "product positioning",
)

text = replace_once(
    text,
    '<td width="25%" align="center"><strong>🚓 Read the fleet</strong><br><sub>See response codes, availability, hidden batches and unit demand in context.</sub></td>',
    '<td width="25%" align="center"><strong>🚓 Read the fleet</strong><br><sub>See response codes, custom vehicle classes, availability, hidden batches and unit demand in context.</sub></td>',
    "fleet value card",
)

spotlight = '''| Review version history | [Changelog](CHANGELOG.md) |

## Specialist fleet intelligence

MissionChief can show the same base vehicle type for units with completely different operational purposes. **Custom Vehicle Badges restores that missing identity directly inside Available Units.**

<div align="center">

### `IRV` · `[Railway Police Officer]`

<sub>Native vehicle type retained. Own Vehicle Category exposed. Specialist dispatch intent immediately visible.</sub>

</div>

<table>
<tr>
<td width="33%" align="center"><strong>🎯 Identify the role</strong><br><sub>Own Vehicle Categories appear beside the native type instead of replacing it.</sub></td>
<td width="33%" align="center"><strong>🔒 Respect dispatch rules</strong><br><sub>Category-only vehicles remain visually distinct without the Toolkit selecting or dispatching them.</sub></td>
<td width="33%" align="center"><strong>🧠 Build better matching</strong><br><sub>Stable vehicle-ID classification gives Mission Requirements the correct foundation for specialist capability logic.</sub></td>
</tr>
</table>

> [!NOTE]
> Badges are compact, theme-aware and automatically restored after MissionChief or LSSM filters, sorts or replaces the Available Units list. Vehicles without an Own Vehicle Category remain untouched.

## Operational systems'''

text = replace_once(
    text,
    "| Review version history | [Changelog](CHANGELOG.md) |\n\n## Operational systems",
    spotlight,
    "specialist fleet spotlight",
)

text = replace_once(
    text,
    "| **Mission Requirements** | Adds a live, normal-flow matrix of missing, en-route, still-needed and selected capacity above MissionChief dispatch controls. |",
    "| **Mission Requirements** | Adds a live, normal-flow matrix of required, on-site, responding, selected and still-needed capacity above MissionChief dispatch controls. |",
    "mission requirements capability wording",
)

text = replace_once(
    text,
    "| **Vehicle Code Status** | Summarises the live fleet by response code, description and count. |\n| **Auto-load all vehicles** | Activates MissionChief's native hidden-vehicle batch control when enabled. |",
    "| **Vehicle Code Status** | Summarises the live fleet by response code, description and count. |\n| **Custom Vehicle Badges** | Shows each Own Vehicle Category beside the native type in Available Units—such as `IRV [Railway Police Officer]`—without changing selection or dispatch behaviour. |\n| **Auto-load all vehicles** | Activates MissionChief's native hidden-vehicle batch control when enabled. |",
    "fleet capability table",
)

text = replace_once(
    text,
    "- Live Mission Requirements matrix with selected and en-route reconciliation",
    "- Live Mission Requirements matrix with on-site, responding, selected and still-needed reconciliation",
    "mission inventory wording",
)

text = replace_once(
    text,
    "- Vehicle Code Status panel and keyboard shortcut\n- Transport demand counts",
    "- Vehicle Code Status panel and keyboard shortcut\n- Custom Vehicle Badges for Own Vehicle Categories in Available Units\n- Stable vehicle-ID classification for specialist capability logic\n- Transport demand counts",
    "fleet inventory additions",
)

# Structural checks keep the mixed Markdown/HTML landing page safe.
for tag in ("div", "table", "tr", "td", "details"):
    opened = len(re.findall(fr"<{tag}(?:\s|>)", text, flags=re.IGNORECASE))
    closed = len(re.findall(fr"</{tag}>", text, flags=re.IGNORECASE))
    if opened != closed:
        raise AssertionError(f"Unbalanced <{tag}> tags: {opened} open, {closed} closed")

required = [
    "## Specialist fleet intelligence",
    "### `IRV` · `[Railway Police Officer]`",
    "**Custom Vehicle Badges**",
    "Stable vehicle-ID classification gives Mission Requirements the correct foundation",
    "required, on-site, responding, selected and still-needed capacity",
    "[#specialist-fleet-intelligence]" if False else "(#specialist-fleet-intelligence)",
]
for marker in required:
    if marker not in text:
        raise AssertionError(f"Missing README marker: {marker}")

if text.count("## Specialist fleet intelligence") != 1:
    raise AssertionError("Specialist fleet section must appear exactly once")
if text.count("IRV [Railway Police Officer]") < 1:
    raise AssertionError("Compact custom category example is missing")
if "specialist custom-category matching is already complete" in text:
    raise AssertionError("README must not overclaim Matrix integration")

README.write_text(text, encoding="utf-8")
print("README Custom Vehicle Badges refresh passed")
