#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
POLICY = ROOT / ".github/userscript-audit-policy.json"

CONFLICT = re.compile(r"^(?:<<<<<<< .+|=======|>>>>>>> .+)$", re.M)
ID_PATTERNS = [
    re.compile(r'''\bid\s*=\s*["']([A-Za-z][\w:.-]*)["']'''),
    re.compile(r'''\.id\s*=\s*["']([A-Za-z][\w:.-]*)["']'''),
    re.compile(r'''setAttribute\(\s*["']id["']\s*,\s*["']([A-Za-z][\w:.-]*)["']\s*\)'''),
]
SELECTOR = re.compile(r'''(?:querySelector(?:All)?|matches|closest)\(\s*([`"'])(.*?)\1\s*\)''', re.S)
KEY = re.compile(r'''(?:event|e|ev)\.(?:key|code)\s*===?\s*["']([^"']+)["']''')
WEBHOOK = re.compile(r"https://(?:discord(?:app)?\.com/api/webhooks|hooks\.slack\.com/services)/[^\s\"']+", re.I)
TOKENS = {
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
URL = re.compile(r'''https?://[^\s"'`<>]+''')

@dataclass
class Finding:
    severity: str
    code: str
    message: str
    subject: str = ""


def line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def source_line(text: str, offset: int) -> str:
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    return text[start: len(text) if end < 0 else end]


def audit(text: str, policy: dict) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    allowed_ids = set(policy.get("allowedDuplicateIds", []))
    allowed_hosts = set(policy.get("allowedUrlHosts", []))
    ignored_selectors = set(policy.get("ignoredSelectors", []))

    if CONFLICT.search(text):
        out.append(Finding("failure", "merge-conflict", "Unresolved merge-conflict marker found."))

    ids: dict[str, list[int]] = {}
    for pattern in ID_PATTERNS:
        for m in pattern.finditer(text):
            if "includes(" in source_line(text, m.start()):
                continue
            ids.setdefault(m.group(1), []).append(line(text, m.start()))
    duplicates = {k: sorted(set(v)) for k, v in ids.items() if len(v) > 1}
    for value, lines in sorted(duplicates.items()):
        if value not in allowed_ids:
            out.append(Finding("failure", "duplicate-dom-id", f"DOM id is defined at multiple source locations: {lines}.", value))

    invalid = []
    selectors = list(SELECTOR.finditer(text))
    for m in selectors:
        value = m.group(2).strip()
        if not value or value in ignored_selectors or "${" in value:
            continue
        reason = None
        if value.count("[") != value.count("]"): reason = "unbalanced attribute brackets"
        elif value.count("(") != value.count(")"): reason = "unbalanced parentheses"
        elif value.endswith(("#", ".", ",", ">", "+", "~")): reason = "incomplete selector suffix"
        elif re.search(r"#[0-9]", value): reason = "unescaped numeric id selector"
        if reason:
            record = {"selector": value[:160], "line": line(text, m.start()), "reason": reason}
            invalid.append(record)
            out.append(Finding("failure", "malformed-selector", f"{reason} at line {record['line']}.", record["selector"]))

    keys: dict[str, list[int]] = {}
    for m in KEY.finditer(text):
        keys.setdefault(m.group(1).casefold(), []).append(line(text, m.start()))
    reused = {k: sorted(set(v)) for k, v in keys.items() if len(v) > 1}
    for value, lines in sorted(reused.items()):
        out.append(Finding("warning", "shortcut-reuse", f"Keyboard key is handled at multiple source locations: {lines}. Review for conflicting actions.", value))

    for m in WEBHOOK.finditer(text):
        if m.group(0).rstrip("),.;").endswith("/..."):
            continue
        out.append(Finding("failure", "embedded-webhook", "A live webhook URL appears embedded in the userscript.", f"line {line(text, m.start())}"))
    for code, pattern in TOKENS.items():
        for m in pattern.finditer(text):
            out.append(Finding("failure", code, "Credential-like material appears embedded in the userscript.", f"line {line(text, m.start())}"))

    urls = sorted(set(URL.findall(text)))
    unknown = []
    for value in urls:
        host = (urlparse(value.rstrip("),.;")).hostname or "").casefold()
        if host and host not in allowed_hosts:
            unknown.append(host)
    for host in sorted(set(unknown)):
        out.append(Finding("warning", "unreviewed-url-host", "URL host is not in the reviewed allowlist.", host))

    return out, {
        "definedDomIds": len(ids), "duplicateDomIds": duplicates,
        "literalSelectorCalls": len(selectors), "invalidSelectors": invalid,
        "literalShortcutChecks": sum(map(len, keys.values())), "shortcutReuse": reused,
        "discoveredUrls": len(urls), "unexpectedUrlHosts": sorted(set(unknown)),
    }


def reports(findings: list[Finding], metrics: dict, json_path: Path, md_path: Path) -> None:
    failures = [f for f in findings if f.severity == "failure"]
    warnings = [f for f in findings if f.severity == "warning"]
    json_path.write_text(json.dumps({"schemaVersion":1,"summary":{"failures":len(failures),"warnings":len(warnings)},"metrics":metrics,"findings":[asdict(f) for f in findings]}, indent=2)+"\n", encoding="utf-8")
    lines = ["# Userscript structural audit", "", f"- Failures: **{len(failures)}**", f"- Warnings: **{len(warnings)}**", f"- DOM IDs discovered: **{metrics['definedDomIds']}**", f"- Literal selector calls: **{metrics['literalSelectorCalls']}**", ""]
    if findings:
        lines += ["## Findings", ""]
        for f in findings:
            suffix = f" — `{f.subject}`" if f.subject else ""
            lines.append(f"- **{f.severity.upper()} · {f.code}**{suffix}: {f.message}")
    else: lines.append("No structural findings.")
    md_path.write_text("\n".join(lines)+"\n", encoding="utf-8")


def self_test() -> None:
    policy = {"allowedDuplicateIds":[],"allowedUrlHosts":["example.com","discord.com"],"ignoredSelectors":[]}
    bad = '''const a='<div id="dup"></div>';
const b='<span id="dup"></span>';
node.querySelector("div["); const hook="https://discord.com/api/webhooks/1/secret"; if(event.key==="v"){} if(e.key==="V"){}'''
    findings, _ = audit(bad, policy)
    assert {"duplicate-dom-id","malformed-selector","embedded-webhook","shortcut-reuse"} <= {f.code for f in findings}
    good = '''if(!source.includes('id="unique"')){} const a='<div id="unique"></div>'; node.querySelector("div[data-id='x']"); const u="https://example.com/a"; const p="https://discord.com/api/webhooks/...";'''
    findings, _ = audit(good, policy)
    assert not [f for f in findings if f.severity == "failure"]
    print("Structural auditor self-tests passed.")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=SOURCE); p.add_argument("--policy", type=Path, default=POLICY)
    p.add_argument("--json-output", type=Path, default=Path("userscript-audit.json")); p.add_argument("--markdown-output", type=Path, default=Path("userscript-audit.md")); p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test: self_test(); return 0
    findings, metrics = audit(a.source.read_text(encoding="utf-8"), json.loads(a.policy.read_text(encoding="utf-8")))
    reports(findings, metrics, a.json_output, a.markdown_output)
    print(json.dumps({"failures":sum(f.severity=="failure" for f in findings),"warnings":sum(f.severity=="warning" for f in findings),**metrics}, indent=2))
    return 1 if any(f.severity == "failure" for f in findings) else 0

if __name__ == "__main__": raise SystemExit(main())
