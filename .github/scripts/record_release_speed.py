#!/usr/bin/env python3
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--history", type=Path, default=Path("status/release-speed-history.json"))
for name in ("version","source","pr","pr_created","merged","implementation_ready","validation_completed","release_started","github_release","discord","verified","implementation_to_green","green_to_merge","pr_to_verified","merge_to_github","merge_to_verified","release_workflow","first_party","backup","discord_seconds","attempts"):
    p.add_argument("--"+name.replace("_","-"), dest=name, default="")
a=p.parse_args()
def n(v): return None if v in ("","null") else int(v)
path=a.history
data=json.loads(path.read_text(encoding="utf-8"))
data["schemaVersion"]=2
for previous in data.get("releases",[]):
    if "sourceSha256" in previous:
        previous["recordedCommit"]=previous.pop("sourceSha256")
record={
    "version":a.version,
    "pipelineVersion":4,
    "benchmarkClass":"normal",
    "includeInHotfixBaseline":True,
    "candidateCommit":a.source,
    "pullRequest":n(a.pr),
    "prCreatedAt":a.pr_created or None,
    "mergedAt":a.merged or None,
    "implementationReadyAt":a.implementation_ready or None,
    "validationCompletedAt":a.validation_completed or None,
    "releaseStartedAt":a.release_started,
    "githubReleaseAt":a.github_release,
    "discordPostedAt":a.discord,
    "verifiedAt":a.verified,
    "durationsSeconds":{
        "implementationToGreen":n(a.implementation_to_green),
        "greenToMerge":n(a.green_to_merge),
        "prToVerified":n(a.pr_to_verified),
        "mergeToGitHubRelease":n(a.merge_to_github),
        "mergeToVerified":n(a.merge_to_verified),
        "releaseWorkflow":n(a.release_workflow),
        "firstPartyPropagation":n(a.first_party),
        "privateBackup":n(a.backup),
        "discordAfterGitHubRelease":n(a.discord_seconds),
    },
    "distributionAttempts":n(a.attempts),
}
data["releases"]=[r for r in data["releases"] if r.get("version")!=a.version]+[record]
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
