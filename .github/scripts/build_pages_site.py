#!/usr/bin/env python3
'''Build the MissionChief Map Command Toolkit GitHub Pages site.

The builder intentionally uses only the Python standard library. It treats
version-controlled JSON, the release dashboard and CHANGELOG.md as source data,
then emits a deterministic static site under _site/.
'''
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "_site"
DATA_PATH = ROOT / "docs" / "site-data.json"
DASHBOARD_PATH = ROOT / "status" / "release-dashboard.json"
SETTINGS_PATH = ROOT / ".github" / "release-settings.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
ASSET_SOURCE = ROOT / "docs" / "site-assets"

REQUIRED_PAGES = {
    "index.html",
    "features/index.html",
    "themes/index.html",
    "docs/index.html",
    "changelog/index.html",
    "status/index.html",
    "404.html",
    "assets/site.css",
    "assets/site.js",
    "data/status.json",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def normalise_base_path(value: str) -> str:
    value = (value or "/").strip()
    if not value.startswith("/"):
        value = "/" + value
    if not value.endswith("/"):
        value += "/"
    return re.sub(r"/{2,}", "/", value)


def href(base_path: str, relative: str = "") -> str:
    return base_path + relative.lstrip("/")


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"Site build error: required JSON file is missing: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Site build error: invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Site build error: {path.relative_to(ROOT)} must contain a JSON object")
    return value


def nav_html(data: dict, base_path: str, active: str) -> str:
    items = []
    for item in data["navigation"]:
        current = ' aria-current="page"' if item["path"] == active else ""
        items.append(f'<a href="{esc(href(base_path, item["path"]))}"{current}>{esc(item["label"])}</a>')
    return "\n".join(items)


def page_shell(*, data: dict, dashboard: dict, base_path: str, active: str, title: str, description: str, body: str) -> str:
    project = data["project"]
    version = dashboard.get("latestRelease", {}).get("version") or dashboard.get("currentVersion") or "unknown"
    canonical = project["pages"].rstrip("/") + "/" + active
    if not active:
        canonical = project["pages"]
    navigation = nav_html(data, base_path, active)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#07111f">
  <meta name="description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <title>{esc(title)}</title>
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="stylesheet" href="{esc(href(base_path, "assets/site.css"))}">
  <script defer src="{esc(href(base_path, "assets/site.js"))}"></script>
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{esc(base_path)}" aria-label="{esc(project["name"])} home">
        <span class="brand-mark" aria-hidden="true"><span></span></span>
        <span class="brand-copy">{esc(project["shortName"])}<small>Version {esc(version)} · verified release</small></span>
      </a>
      <button class="nav-toggle" type="button" aria-label="Open navigation" aria-expanded="false" data-nav-toggle>☰</button>
      <nav class="nav" aria-label="Primary navigation" data-nav>
        {navigation}
      </nav>
    </div>
  </header>
  <main id="content">
    {body}
  </main>
  <footer class="footer">
    <div class="container footer-inner">
      <div><strong>{esc(project["name"])}</strong><br>GitHub-controlled releases · Greasy Fork distribution · MIT licence</div>
      <div class="footer-links">
        <a href="{esc(project["repository"])}">GitHub</a>
        <a href="{esc(project["issues"])}">Support</a>
        <a href="{esc(project["releases"])}">Releases</a>
        <a href="{esc(href(base_path, "status/"))}">System status</a>
      </div>
    </div>
  </footer>
</body>
</html>
'''


def status_value(value: object) -> str:
    if value is True:
        return "Verified"
    if value is False:
        return "Not verified"
    text = str(value or "unknown").replace("-", " ").replace("_", " ")
    return " ".join(word.capitalize() for word in text.split())


def health_table(dashboard: dict) -> str:
    status = dashboard.get("status", {})
    rows = [
        ("Canonical validation", status.get("validation", "unknown")),
        ("GitHub Release", status.get("githubRelease", "unknown")),
        ("Greasy Fork", status.get("greasyForkSync", "unknown")),
        ("Private backup", status.get("backup", "unknown")),
        ("Development Discord", status.get("discordDevelopment", "unknown")),
        ("Release Discord", status.get("discordRelease", "unknown")),
        ("Asset audit", status.get("assetAudit", "unknown")),
        ("Release readiness", status.get("releaseReadiness", "unknown")),
    ]
    return "\n".join(
        f"<tr><td>{esc(label)}</td><td><span class=\"health\">Healthy</span></td><td>{esc(status_value(value))}</td></tr>"
        for label, value in rows
    )


def visual_html(kind: str) -> str:
    if kind in {"mission-age", "critical", "inspector"}:
        rows = [("Warehouse Fire", "18H"), ("Rail Incident", "11H"), ("Medical Emergency", "CLEAR")]
        return '<div class="visual"><div class="mini-title">Mission priority</div>' + "".join(
            f'<div class="mini-row"><span class="mini-icon"></span><span>{esc(name)}</span><span class="mini-badge">{esc(age)}</span></div>'
            for name, age in rows
        ) + "</div>"
    if kind == "feed":
        return '<div class="visual"><div class="mini-title">Major incident feed</div><div class="mini-row"><span class="mini-icon"></span><span>Major fire · EH12</span><span class="mini-badge">ZOOM</span></div><div class="mini-row"><span class="mini-icon"></span><span>Rail disruption · G1</span><span class="mini-badge">OPEN</span></div></div>'
    if kind in {"vehicle-code", "transport", "focus"}:
        return '<div class="visual"><div class="mini-title">Vehicle state</div><div class="mini-row"><span>Code 1</span><span>Available</span><span class="mini-badge">42</span></div><div class="mini-row"><span>Code 3</span><span>En-route</span><span class="mini-badge">18</span></div><div class="mini-row"><span>Code 6</span><span>At scene</span><span class="mini-badge">27</span></div></div>'
    if kind in {"coverage", "rings"}:
        return '<div class="visual"><span class="map-grid"></span><span class="ring r1"></span><span class="ring r2"></span><span class="ring r3"></span><span class="pin"></span></div>'
    if kind == "bookmarks":
        return '<div class="visual"><div class="mini-title">Smart bookmarks</div><div class="bookmark-row"><span class="bookmark">EDI</span><span class="bookmark">FIFE</span><span class="bookmark">GLA</span><span class="bookmark">STIR</span><span class="bookmark">ABDN</span></div><p>Full names remain available on hover or long press.</p></div>'
    if kind in {"credits", "finance"}:
        return '<div class="visual"><div class="mini-title">Financial command</div><div class="big-number">£184.6k</div><div class="mini-row"><span>Income</span><span>Today</span><span class="mini-badge">+£24.8k</span></div><div class="mini-row"><span>Net</span><span>This week</span><span class="mini-badge">+£91.2k</span></div></div>'
    if kind == "payout":
        return '<div class="visual"><div class="payout-banner"><span>MISSION COMPLETE</span><strong>£18,500</strong><small>Verified payout</small></div></div>'
    if kind == "modes":
        return '<div class="visual"><div class="mini-title">Responsive modes</div><div class="mode-devices"><span class="device desktop"></span><span class="device tablet"></span><span class="device phone"></span></div></div>'
    if kind == "settings":
        return '<div class="visual"><div class="mini-title">Toolkit settings</div><div class="mini-row"><span>Theme</span><span>Map Command</span><span class="mini-badge">ON</span></div><div class="mini-row"><span>Tablet Mode</span><span>Responsive</span><span class="mini-badge">OFF</span></div><div class="mini-row"><span>Export</span><span>Timestamped</span><span class="mini-badge">SAVE</span></div></div>'
    return '<div class="visual"><div class="mini-title">Toolkit interface</div></div>'


def feature_card(feature: dict) -> str:
    tags = " ".join(feature.get("tags", []))
    details = "".join(f"<li>{esc(item)}</li>" for item in feature.get("details", []))
    tag_html = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in feature.get("tags", []))
    return f'''<article class="card feature-card" data-feature-card data-tags="{esc(tags)}">
  {visual_html(feature.get("visual", ""))}
  <div class="feature-copy">
    <h3>{esc(feature["name"])}</h3>
    <p>{esc(feature["summary"])}</p>
    <ul>{details}</ul>
    <div class="tag-row">{tag_html}</div>
  </div>
</article>'''


def home_page(data: dict, dashboard: dict, settings: dict, base_path: str) -> str:
    project = data["project"]
    release = dashboard.get("latestRelease", {})
    assets = dashboard.get("assets", {})
    install = settings.get("greasyFork", {}).get("installUrl", "#")
    script_url = settings.get("greasyFork", {}).get("scriptUrl", "#")
    featured = []
    for category in data["featureCategories"][:4]:
        feature = category["features"][0]
        featured.append(
            f'<a class="card card-link" href="{esc(href(base_path, "features/"))}"><span class="eyebrow">{esc(category["name"])}</span><h3>{esc(feature["name"])}</h3><p>{esc(feature["summary"])}</p></a>'
        )
    modes = "".join(
        f'<article class="card"><h3>{esc(mode["name"])}</h3><p>{esc(mode["summary"])}</p><div class="tag-row"><span class="tag">{esc(mode["bestFor"])}</span></div></article>'
        for mode in data["modes"]
    )
    theme_cards = []
    for theme in data["themes"][:3]:
        swatches = "".join(f'<span class="swatch" style="background:{esc(colour)}"></span>' for colour in theme["palette"])
        theme_cards.append(f'<a class="card card-link" href="{esc(href(base_path, "themes/"))}"><h3>{esc(theme["name"])}</h3><p>{esc(theme["description"])}</p><div class="palette">{swatches}</div></a>')
    pipeline_html = "".join(f'<div class="pipeline-step">{esc(item)}</div>' for item in ["GitHub source", "Validation", "GitHub Release", "Greasy Fork", "Private backup", "Discord"])
    body = f'''
<section class="hero">
  <div class="container">
    <span class="eyebrow">MissionChief operational interface</span>
    <h1>Command the map.<br>See what matters.</h1>
    <p class="hero-copy">{esc(project["description"])}</p>
    <div class="actions">
      <a class="button primary" href="{esc(install)}">Install or update Toolkit</a>
      <a class="button" href="{esc(script_url)}">View on Greasy Fork</a>
      <a class="button" href="{esc(href(base_path, "docs/"))}">Open documentation</a>
    </div>
    <div class="release-strip" aria-label="Current release status">
      <div class="stat"><span class="stat-label">Current version</span><span class="stat-value">{esc(release.get("version", dashboard.get("currentVersion", "unknown")))}</span></div>
      <div class="stat"><span class="stat-label">Release status</span><span class="stat-value"><span class="status-dot"></span>Verified</span></div>
      <div class="stat"><span class="stat-label">Hosted assets</span><span class="stat-value">{esc(assets.get("discoveredFiles", 0))} monitored</span></div>
      <div class="stat"><span class="stat-label">Missing assets</span><span class="stat-value">{esc(assets.get("missingReferencedPaths", 0))}</span></div>
      <div class="stat"><span class="stat-label">Last verified</span><span class="stat-value" data-iso-date="{esc(release.get("completedAt", dashboard.get("lastUpdated", "")))}">{esc(release.get("completedAt", dashboard.get("lastUpdated", "unknown")))}</span></div>
    </div>
  </div>
</section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Operational systems</span><h2>One Toolkit, several command layers</h2></div><p>The interface remains map-first. Large systems are constructed on demand and can be enabled only when they are operationally useful.</p></div><div class="grid two">{''.join(featured)}</div><div class="actions"><a class="button" href="{esc(href(base_path, "features/"))}">Browse all features</a></div></div></section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Responsive operation</span><h2>Desktop, tablet and iOS</h2></div><p>Persistent settings and purpose-built layouts keep the Toolkit usable across large maps, touch screens and Safari on iPhone.</p></div><div class="grid three">{modes}</div></div></section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Interface themes</span><h2>Distinct skins, consistent controls</h2></div><p>Theme styling changes the presentation layer without changing the underlying operational workflow.</p></div><div class="grid three">{''.join(theme_cards)}</div></div></section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Verified distribution</span><h2>GitHub to users, with recovery built in</h2></div><p>Public announcements occur only after the Greasy Fork version is live and the validated release has been backed up.</p></div><div class="pipeline">{pipeline_html}</div><div class="actions"><a class="button" href="{esc(href(base_path, "status/"))}">Open live release status</a><a class="button" href="{esc(project["releases"])}">GitHub Releases</a></div></div></section>
'''
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="", title=project["name"], description=project["description"], body=body)


def features_page(data: dict, dashboard: dict, base_path: str) -> str:
    categories = []
    for index, category in enumerate(data["featureCategories"]):
        cards = "".join(feature_card(feature) for feature in category["features"])
        categories.append(f'''<section class="feature-category" id="category-{index}">
  <div class="section-heading"><div><span class="eyebrow">Feature group</span><h2>{esc(category["name"])}</h2></div><p>{esc(category["description"])}</p></div>
  <div class="grid">{cards}</div>
</section>''')
    body = f'''<section class="page-hero"><div class="container"><span class="eyebrow">Feature catalogue</span><h1>Operational capability, grouped by purpose</h1><p>Search the current Toolkit systems. The catalogue describes user-facing behaviour rather than internal implementation details.</p><input class="search-box" type="search" placeholder="Filter features, for example: missions, finance, iOS" aria-label="Filter features" data-feature-filter></div></section>
<section class="section compact"><div class="container">{''.join(categories)}<div class="no-results" data-no-results>No feature matches that filter.</div></div></section>'''
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="features/", title=f'Features · {data["project"]["name"]}', description="Complete MissionChief Map Command Toolkit feature catalogue.", body=body)


def themes_page(data: dict, dashboard: dict, base_path: str) -> str:
    theme_cards = []
    for theme in data["themes"]:
        swatches = "".join(f'<span class="swatch" style="background:{esc(colour)}"></span>' for colour in theme["palette"])
        theme_cards.append(f'''<article class="card theme-card">
  <div class="theme-preview theme-{esc(theme["slug"])}"><div class="theme-ui"><div class="bar"></div><div class="theme-buttons"><span></span><span></span><span></span><span></span></div></div></div>
  <div class="theme-info"><h3>{esc(theme["name"])}</h3><p>{esc(theme["description"])}</p><div class="palette">{swatches}</div></div>
</article>''')
    payout = "".join(f'<span class="tag">{esc(name)}</span>' for name in data["payoutThemes"])
    roadmap = "".join(f'<div class="card"><h3>{esc(item)}</h3><p>Planned verified capture for GitHub, Greasy Fork and this documentation site.</p></div>' for item in data["mediaRoadmap"])
    body = f'''<section class="page-hero"><div class="container"><span class="eyebrow">Visual gallery</span><h1>Five interface identities. One control system.</h1><p>These live CSS previews show the design language of each full interface theme. The userscript themes themselves are unchanged by this documentation site.</p></div></section>
<section class="section compact"><div class="container"><div class="theme-grid">{''.join(theme_cards)}</div></div></section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Mission completion</span><h2>Payout presentation library</h2></div><p>Completion banners can use a separate presentation theme and optional hosted audio.</p></div><div class="card"><div class="tag-row">{payout}</div></div></div></section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Media programme</span><h2>Screenshot and demonstration roadmap</h2></div><p>Captured media will be added without replacing stable public assets used by installed Toolkit versions.</p></div><div class="grid two">{roadmap}</div></div></section>'''
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="themes/", title=f'Themes · {data["project"]["name"]}', description="Visual gallery for Toolkit interface and payout themes.", body=body)


def docs_page(data: dict, dashboard: dict, settings: dict, base_path: str) -> str:
    nav, sections = [], []
    for index, chapter in enumerate(data["documentation"]):
        anchor = f"chapter-{index}"
        nav.append(f'<a href="#{anchor}">{esc(chapter["title"])}</a>')
        parts = [f'<section class="docs-block" id="{anchor}"><h2>{esc(chapter["title"])}</h2>']
        for section in chapter["sections"]:
            parts.append(f'<h3>{esc(section["heading"])}</h3><p>{esc(section["body"])}</p>')
        parts.append("</section>")
        sections.append("".join(parts))
    shortcuts = "".join(f'<div class="shortcut"><kbd>{esc(item["key"])}</kbd><span>{esc(item["action"])}</span></div>' for item in data["shortcuts"])
    trouble = "".join(f'<article class="card trouble-card"><h3>{esc(item["problem"])}</h3><ol>{"".join(f"<li>{esc(step)}</li>" for step in item["steps"])}</ol></article>' for item in data["troubleshooting"])
    issues = "".join(f'<article class="card issue-card {"watch" if item["level"] == "watch" else ""}"><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></article>' for item in data["knownIssues"])
    install = settings.get("greasyFork", {}).get("installUrl", "#")
    body = f'''<section class="page-hero"><div class="container"><span class="eyebrow">Documentation centre</span><h1>Install, operate and diagnose the Toolkit</h1><p>Start with the operating model, then use the feature guidance, confirmed shortcuts and troubleshooting paths below.</p><div class="actions"><a class="button primary" href="{esc(install)}">Install current release</a><a class="button" href="{esc(data["project"]["issues"])}">Open support form</a></div></div></section>
<section class="section compact"><div class="container docs-layout"><aside class="docs-nav" aria-label="Documentation chapters">{''.join(nav)}<a href="#shortcuts">Keyboard shortcuts</a><a href="#troubleshooting">Troubleshooting</a><a href="#known-issues">Known issues</a></aside><div>{''.join(sections)}
<section class="docs-block" id="shortcuts"><h2>Keyboard shortcuts</h2><p>Confirmed global shortcuts in the current Toolkit release. Inputs and editable fields remain protected from accidental activation.</p><div class="shortcut-grid">{shortcuts}</div></section>
<section class="docs-block" id="troubleshooting"><h2>Troubleshooting</h2><div class="grid">{trouble}</div><div class="callout">Performance reports should include the Toolkit version, browser, userscript manager, device, mission and vehicle scale, enabled features and <code>window.__MCMS_STARTUP_METRICS__</code>.</div></section>
<section class="docs-block" id="known-issues"><h2>Known issues and operational notes</h2><div class="grid">{issues}</div></section>
</div></div></section>'''
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="docs/", title=f'Documentation · {data["project"]["name"]}', description="Installation, feature guidance, shortcuts and troubleshooting for the Toolkit.", body=body)


def parse_changelog(text: str) -> list[dict]:
    releases, current, subsection = [], None, None
    for raw in text.splitlines():
        line = raw.strip()
        release = re.match(r"^## \[(?P<version>[^\]]+)\](?:\s+-\s+(?P<date>\d{4}-\d{2}-\d{2}))?$", line)
        if release:
            current = {"version": release.group("version"), "date": release.group("date"), "sections": []}
            releases.append(current)
            subsection = None
            continue
        heading = re.match(r"^###\s+(.+)$", line)
        if heading and current is not None:
            subsection = {"title": heading.group(1), "items": []}
            current["sections"].append(subsection)
            continue
        if line.startswith("- ") and subsection is not None:
            subsection["items"].append(line[2:])
    return releases


def changelog_page(data: dict, dashboard: dict, changelog_text: str, base_path: str) -> str:
    release_html = []
    for release in parse_changelog(changelog_text):
        if release["version"].casefold() == "unreleased" and not any(section["items"] for section in release["sections"]):
            continue
        sections = []
        for section in release["sections"]:
            items = "".join(f"<li>{esc(item)}</li>" for item in section["items"])
            sections.append(f'<h3>{esc(section["title"])}</h3><ul>{items}</ul>')
        date = f' <small>· {esc(release["date"])}</small>' if release.get("date") else ""
        release_html.append(f'<article class="changelog-release"><h2>Version {esc(release["version"])}{date}</h2>{"".join(sections)}</article>')
    body = f'<section class="page-hero"><div class="container"><span class="eyebrow">Release history</span><h1>Validated Toolkit changes</h1><p>This page is generated directly from the canonical CHANGELOG.md used by the release pipeline.</p></div></section><section class="section compact"><div class="container">{"".join(release_html)}</div></section>'
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="changelog/", title=f'Changelog · {data["project"]["name"]}', description="MissionChief Map Command Toolkit release history.", body=body)


def status_page(data: dict, dashboard: dict, base_path: str) -> str:
    release = dashboard.get("latestRelease", {})
    assets = dashboard.get("assets", {})
    hash_value = release.get("sha256") or dashboard.get("source", {}).get("validatedSha256") or "unknown"
    body = f'''<section class="page-hero"><div class="container"><span class="eyebrow">Release control panel</span><h1>Current version {esc(release.get("version", dashboard.get("currentVersion", "unknown")))}</h1><p>The status page is generated from the same machine-readable dashboard used by release, recovery and Discord automation.</p><div class="actions"><a class="button" href="{esc(release.get("githubRelease", data["project"]["releases"]))}">Open current GitHub Release</a><button class="button" type="button" data-copy="{esc(hash_value)}">Copy SHA-256</button></div></div></section>
<section class="section compact"><div class="container"><div class="card"><table class="status-table"><thead><tr><th>System</th><th>Health</th><th>Recorded state</th></tr></thead><tbody>{health_table(dashboard)}</tbody></table></div></div></section>
<section class="section"><div class="container"><div class="grid three"><div class="card"><span class="stat-label">Validated SHA-256</span><p><code>{esc(hash_value)}</code></p></div><div class="card"><span class="stat-label">Media assets</span><p class="big-number">{esc(assets.get("discoveredFiles", 0))}</p><p>{esc(assets.get("referencedPaths", 0))} referenced hosted paths.</p></div><div class="card"><span class="stat-label">Last dashboard update</span><p data-iso-date="{esc(dashboard.get("lastUpdated", ""))}">{esc(dashboard.get("lastUpdated", "unknown"))}</p><p>Missing referenced paths: {esc(assets.get("missingReferencedPaths", 0))}</p></div></div></div></section>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Publication sequence</span><h2>Release integrity path</h2></div><p>Discord follows verified distribution and private backup. Recovery tooling can repair individual stages without creating duplicate releases.</p></div><div class="pipeline">{''.join(f'<div class="pipeline-step">{esc(item)}</div>' for item in ["Canonical source", "CI validation", "GitHub Release", "Greasy Fork", "Private backup", "Discord"])}</div></div></section>'''
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="status/", title=f'Status · {data["project"]["name"]}', description="Live Toolkit release and distribution status.", body=body)


def not_found_page(data: dict, dashboard: dict, base_path: str) -> str:
    body = f'<section class="hero"><div class="container"><span class="eyebrow">404</span><h1>That command route does not exist.</h1><p class="hero-copy">Return to the Toolkit control centre or open the documentation index.</p><div class="actions"><a class="button primary" href="{esc(base_path)}">Return home</a><a class="button" href="{esc(href(base_path, "docs/"))}">Documentation</a></div></div></section>'
    return page_shell(data=data, dashboard=dashboard, base_path=base_path, active="", title=f'Not found · {data["project"]["name"]}', description="Page not found.", body=body)


def write_page(output: Path, relative: str, content: str) -> None:
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def validate_output(output: Path, base_path: str) -> None:
    missing = sorted(path for path in REQUIRED_PAGES if not (output / path).is_file())
    if missing:
        raise SystemExit("Site build error: missing output files: " + ", ".join(missing))
    failures = []
    for page in output.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        if "{{" in text or "}}" in text:
            failures.append(f"{page.relative_to(output)} contains an unresolved template token")
        if "<title></title>" in text:
            failures.append(f"{page.relative_to(output)} has an empty title")
        for match in re.finditer(r'(?:href|src)="([^"]+)"', text):
            url = html.unescape(match.group(1))
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not url.startswith(base_path):
                failures.append(f"{page.relative_to(output)} contains a non-base-path internal URL: {url}")
                continue
            local = url[len(base_path):].split("#", 1)[0].split("?", 1)[0]
            if not local:
                target = output / "index.html"
            elif local.endswith("/"):
                target = output / local / "index.html"
            else:
                target = output / local
            if not target.exists():
                failures.append(f"{page.relative_to(output)} links to missing output: {url}")
    if failures:
        raise SystemExit("Site validation failed:\n- " + "\n- ".join(sorted(set(failures))))


def build(output: Path, base_path: str) -> None:
    data = load_json(DATA_PATH)
    dashboard = load_json(DASHBOARD_PATH)
    settings = load_json(SETTINGS_PATH)
    changelog_text = CHANGELOG_PATH.read_text(encoding="utf-8")
    required_project_keys = {"name", "shortName", "description", "repository", "issues", "releases", "pages"}
    missing = sorted(required_project_keys - set(data.get("project", {})))
    if missing:
        raise SystemExit("Site build error: site-data project section is missing: " + ", ".join(missing))
    if not data.get("featureCategories") or not data.get("themes") or not data.get("shortcuts"):
        raise SystemExit("Site build error: feature, theme and shortcut catalogues must not be empty")
    if not dashboard.get("latestRelease", {}).get("version"):
        raise SystemExit("Site build error: release dashboard has no latestRelease.version")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(ASSET_SOURCE, output / "assets")
    write_page(output, "index.html", home_page(data, dashboard, settings, base_path))
    write_page(output, "features/index.html", features_page(data, dashboard, base_path))
    write_page(output, "themes/index.html", themes_page(data, dashboard, base_path))
    write_page(output, "docs/index.html", docs_page(data, dashboard, settings, base_path))
    write_page(output, "changelog/index.html", changelog_page(data, dashboard, changelog_text, base_path))
    write_page(output, "status/index.html", status_page(data, dashboard, base_path))
    write_page(output, "404.html", not_found_page(data, dashboard, base_path))
    write_page(output, "data/status.json", json.dumps(dashboard, indent=2) + "\n")
    write_page(output, ".nojekyll", "")
    write_page(output, "robots.txt", "User-agent: *\nAllow: /\n")
    sitemap_urls = [data["project"]["pages"].rstrip("/") + "/" + item["path"] for item in data["navigation"]]
    write_page(output, "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{esc(url)}</loc></url>\n" for url in sitemap_urls) + "</urlset>\n")
    validate_output(output, base_path)
    file_count = sum(1 for path in output.rglob("*") if path.is_file())
    print(json.dumps({
        "result": "passed",
        "version": dashboard["latestRelease"]["version"],
        "output": str(output),
        "basePath": base_path,
        "files": file_count,
        "featureCategories": len(data["featureCategories"]),
        "features": sum(len(category["features"]) for category in data["featureCategories"]),
        "themes": len(data["themes"]),
        "shortcuts": len(data["shortcuts"]),
    }, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-path", default="/missionchief-toolkit-assets/")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build(args.output.resolve(), normalise_base_path(args.base_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
