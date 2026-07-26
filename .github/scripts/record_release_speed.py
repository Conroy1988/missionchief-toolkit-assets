#!/usr/bin/env python3
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser()
for name in ("version","source","pr","pr_created","merged","release_started","github_release","discord","verified","pr_to_verified","merge_to_github","merge_to_verified","release_workflow","greasyfork","backup","discord_seconds","attempts"):
    p.add_argument("--"+name.replace("_","-"), dest=name, default="")
a=p.parse_args()
def n(v): return None if v in ("","null") else int(v)
path=Path("status/release-speed-history.json")
data=json.loads(path.read_text(encoding="utf-8"))
record={"version":a.version,"pipelineVersion":4,"benchmarkClass":"normal","includeInHotfixBaseline":True,"sourceSha256":a.source,"pullRequest":n(a.pr),"prCreatedAt":a.pr_created or None,"mergedAt":a.merged or None,"releaseStartedAt":a.release_started,"githubReleaseAt":a.github_release,"discordPostedAt":a.discord,"verifiedAt":a.verified,"durationsSeconds":{"prToVerified":n(a.pr_to_verified),"mergeToGitHubRelease":n(a.merge_to_github),"mergeToVerified":n(a.merge_to_verified),"releaseWorkflow":n(a.release_workflow),"greasyForkPropagation":n(a.greasyfork),"privateBackup":n(a.backup),"discordAfterGitHubRelease":n(a.discord_seconds)},"greasyForkAttempts":n(a.attempts)}
data["releases"]=[r for r in data["releases"] if r.get("version")!=a.version]+[record]
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
