#!/usr/bin/env python3
import json, math, statistics
from pathlib import Path
root=Path(__file__).resolve().parents[2]
data=json.loads((root/"status/release-speed-history.json").read_text(encoding="utf-8"))
def vals(records,key): return [r.get("durationsSeconds",{}).get(key) for r in records if isinstance(r.get("durationsSeconds",{}).get(key),int)]
def pct(v,p):
    if not v:return None
    s=sorted(v);return s[max(0,math.ceil(len(s)*p)-1)]
def med(v): return statistics.median(v) if v else None
def fmt(v):
    if v is None:return "—"
    m,s=divmod(round(v),60);return f"{m}m {s:02d}s" if m else f"{s}s"
base=[r for r in data["releases"] if r.get("pipelineVersion")==3 and r.get("includeInHotfixBaseline")]
v4=[r for r in data["releases"] if r.get("pipelineVersion")==4]
b=vals(base,"prToVerified");f=vals(v4,"prToVerified");implementation=vals(v4,"implementationToGreen")
bm=round(statistics.median(b));target=data["targets"]["normalHotfixPrToVerifiedMedianSeconds"]
lines=[
    "# Release Speed Control","","> Machine-generated exact-candidate release telemetry for Pipeline v4.","",
    "## Headline","",
    f"- **Historical normal-hotfix median:** {fmt(bm)}",
    f"- **Pipeline v4 target median:** {fmt(target)}",
    f"- **Expected reduction:** {round((1-target/bm)*100,1)}%",
    f"- **Expected throughput:** {round(bm/target,1)}×",
    f"- **Measured Pipeline v4 median:** {fmt(med(f))}",
    f"- **Measured implementation-ready → green median:** {fmt(med(implementation))}","",
    "## Statistics","",
    "| Metric | v3 baseline | v4 measured | v4 target |",
    "|---|---:|---:|---:|",
    f"| Implementation-ready → green median | — | {fmt(med(implementation))} | measured only |",
    f"| PR → verified median | {fmt(bm)} | {fmt(med(f))} | {fmt(target)} |",
    f"| PR → verified P90 | {fmt(pct(b,.9))} | {fmt(pct(f,.9))} | {fmt(data['targets']['normalHotfixPrToVerifiedP90Seconds'])} |",
    f"| Merge → verified median | {fmt(med(vals(base,'mergeToVerified')))} | {fmt(med(vals(v4,'mergeToVerified')))} | {fmt(data['targets']['mergeToVerifiedMedianSeconds'])} |","",
    "## Release history","",
    "| Version | Pipeline | Class | Implementation → green | Green → merge | PR → verified | Merge → GitHub | Merge → verified | Greasy Fork | Backup |",
    "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
]
for r in reversed(data["releases"]):
    d=r.get("durationsSeconds",{})
    lines.append(f"| {r.get('version')} | v{r.get('pipelineVersion')} | {r.get('benchmarkClass')} | {fmt(d.get('implementationToGreen'))} | {fmt(d.get('greenToMerge'))} | {fmt(d.get('prToVerified'))} | {fmt(d.get('mergeToGitHubRelease'))} | {fmt(d.get('mergeToVerified'))} | {fmt(d.get('greasyForkPropagation'))} | {fmt(d.get('privateBackup'))} |")
lines += ["","The v8.0.2 binary-transfer exception is retained for transparency but excluded from the normal-hotfix baseline. GitHub Pages is asynchronous and does not block userscript delivery. Null historical fields are displayed as em dashes rather than inferred.",""]
(root/"status/RELEASE_SPEED.md").write_text("\n".join(lines),encoding="utf-8")
