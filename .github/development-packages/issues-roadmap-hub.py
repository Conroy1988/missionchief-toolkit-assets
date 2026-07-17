#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


readme = Path("README.md")
replace_once(
    readme,
    "[Why it exists](#why-it-exists) · [Install](#install-in-under-a-minute) · [Systems](#operational-systems) · [Themes](#seven-interface-systems) · [Devices](#built-for-every-screen) · [Release confidence](#release-confidence) · [Support](#support-and-roadmap)",
    "[Why it exists](#why-it-exists) · [Install](#install-in-under-a-minute) · [Systems](#operational-systems) · [Themes](#seven-interface-systems) · [Devices](#built-for-every-screen) · [Release confidence](#release-confidence) · [Support](#support-and-development)",
)

old_support = """## Support and roadmap

| Route | Use it for |
|---|---|
| [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) | Installation, configuration and feature guidance. |
| [Help and troubleshooting](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/help-and-troubleshooting) | Usage questions and setup problems. |
| [Feature ideas](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/feature-ideas) | Early proposals and community discussion. |
| [Show and tell](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/show-and-tell) | Layouts, themes and operational setups. |
| [GitHub Issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) | Confirmed bugs, regressions and actionable specifications. |
| [Public roadmap](https://github.com/users/Conroy1988/projects) | Current investigation, development and release state. |
"""

new_support = """## Support and development

Choose the route that matches the stage of the request. Early ideas belong in Discussions; confirmed work moves into Issues, where scope, priority, implementation and completion history remain visible.

<div align="center">

[![View planned work](https://img.shields.io/badge/VIEW-PLANNED%20WORK-1D76DB?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aopen+label%3Aroadmap)
[![Report a bug](https://img.shields.io/badge/REPORT-A%20BUG-D73A4A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new/choose)
[![Propose an idea](https://img.shields.io/badge/PROPOSE-AN%20IDEA-7C3AED?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/feature-ideas)
[![Get help](https://img.shields.io/badge/GET-HELP-0F766E?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/help-and-troubleshooting)

</div>

<table>
<tr>
<td width="33%" valign="top"><strong>📘 Use and configure</strong><br><sub>Open the <a href="https://conroy1988.github.io/missionchief-toolkit-assets/">documentation</a> for installation, settings and feature guidance. Use <a href="https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/help-and-troubleshooting">Help and troubleshooting</a> for setup problems.</sub></td>
<td width="33%" valign="top"><strong>💡 Shape what comes next</strong><br><sub>Start early concepts in <a href="https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/feature-ideas">Feature ideas</a>. Once a proposal has clear scope and acceptance criteria, it moves into GitHub Issues.</sub></td>
<td width="33%" valign="top"><strong>🛠️ Track active engineering</strong><br><sub>Use <a href="https://github.com/Conroy1988/missionchief-toolkit-assets/issues">Issues</a> for confirmed bugs and actionable work, then follow linked pull requests and <a href="https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest">releases</a> through delivery.</sub></td>
</tr>
</table>

### Live development views

| View | What it contains |
|---|---|
| **[Planned work](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aopen+label%3Aroadmap)** | Open product and engineering work carrying the `roadmap` label. |
| **[High-priority queue](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aopen+label%3A%22priority%3A+high%22)** | Work explicitly marked for urgent attention. |
| **[Open bugs](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aopen+label%3Abug)** | Confirmed defects and regressions awaiting correction. |
| **[All open issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aopen)** | The complete actionable development backlog. |
| **[Completed work](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aclosed)** | Delivered fixes, features and engineering history. |

> [!IMPORTANT]
> **GitHub Issues is the canonical public roadmap.** The `roadmap` label identifies planned product and engineering work, priority labels determine urgency, and closed issues preserve the completed development record.

### From idea to release

<table>
<tr>
<td width="25%" align="center"><strong>1 · Discuss</strong><br><sub>Explore an early idea in Discussions without committing it to delivery.</sub></td>
<td width="25%" align="center"><strong>2 · Specify</strong><br><sub>Convert confirmed work into an Issue with scope and acceptance criteria.</sub></td>
<td width="25%" align="center"><strong>3 · Prioritise</strong><br><sub>Apply roadmap, type and priority labels to place it in the live queue.</sub></td>
<td width="25%" align="center"><strong>4 · Deliver</strong><br><sub>Link the branch and pull request, validate the change, release when required, then close the Issue.</sub></td>
</tr>
</table>

Community layouts, themes and operational setups remain welcome in [Show and tell](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/show-and-tell).
"""
replace_once(readme, old_support, new_support)

replace_once(
    readme,
    "[Install](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) · [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) · [Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) · [Roadmap](https://github.com/users/Conroy1988/projects)",
    "[Install](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) · [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) · [Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) · [Planned work](https://github.com/Conroy1988/missionchief-toolkit-assets/issues?q=is%3Aissue+state%3Aopen+label%3Aroadmap)",
)

contributing = Path("CONTRIBUTING.md")
old_contributing = """## Development expectations

- Preserve the existing Desktop, Tablet and iOS operating modes.
"""
new_contributing = """## Roadmap and issue flow

- Use **Discussions → Feature ideas** for early concepts that still need community or design exploration.
- Use **GitHub Issues** for confirmed bugs, improvements and actionable technical specifications.
- Apply the `roadmap` label only to planned product or engineering work that belongs in the public development queue.
- Use priority labels to express urgency; do not duplicate scheduling state in a separate roadmap document or Project.
- Link implementation pull requests to their Issue so merged work automatically becomes part of the completed development record.

## Development expectations

- Preserve the existing Desktop, Tablet and iOS operating modes.
"""
replace_once(contributing, old_contributing, new_contributing)
