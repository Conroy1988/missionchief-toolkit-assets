# Repository and dependency audit

> Generated automatically. This audit does not rename, move or delete files.

## Summary

- Repository files: **177**
- Media files: **37**
- GitHub Actions workflows: **29**
- Greasy Fork version: **4.13.1**
- Repository URLs referenced by current script/repository: **33**
- Missing referenced paths: **0**
- Possible one-shot workflows: **18**
- Duplicate media groups: **1**

## Current userscript source

Greasy Fork was read successfully at version **4.13.1**.
No canonical `.user.js` file is assumed until a source file is deliberately imported and validated.

## Referenced public repository paths

- `bf-bad-company-cashout.mp3` — ✅ present
- `cyberpunk-cashout.mp3` — ✅ present
- `factorio-cashout.mp3` — ✅ present
- `fallout-cashout.mp3` — ✅ present
- `financial-intelligence/v1/classification-rules.json` — ✅ present
- `financial-intelligence/v2/audit-policy.json` — ✅ present
- `gta-vice-city-cashout.mp3` — ✅ present
- `help/index.html` — ✅ present
- `james-bond-cashout.mp3` — ✅ present
- `scarface-cashout.mp3` — ✅ present
- `themes/hyrule/audio/hyrule-quest-reward.mp3` — ✅ present
- `themes/hyrule/payout/quest-complete-seal.svg` — ✅ present
- `themes/hyrule/payout/rupee-burst.svg` — ✅ present
- `themes/hyrule/ui/ancient-eye-rune.svg` — ✅ present
- `themes/hyrule/ui/hyrule-command-crest.svg` — ✅ present
- `themes/hyrule/ui/master-sword-shield-silhouette.svg` — ✅ present
- `themes/hyrule/ui/parchment-command-map.svg` — ✅ present
- `themes/hyrule/ui/zonai-energy-ring.svg` — ✅ present
- `themes/james-bond/007-logo.svg` — ✅ present
- `themes/james-bond/payout/daniel-craig-007-portrait.png` — ✅ present
- `themes/james-bond/payout/funds-authorised-seal.svg` — ✅ present
- `themes/james-bond/ui/agent-silhouette.svg` — ✅ present
- `themes/james-bond/ui/classified-dossier-grid.svg` — ✅ present
- `themes/james-bond/ui/gold-divider.svg` — ✅ present
- `themes/james-bond/ui/gunbarrel-reticle.svg` — ✅ present
- `themes/james-bond/ui/mi6-command-seal.svg` — ✅ present
- `themes/umbrella/audio/umbrella-containment-cashout.mp3` — ✅ present
- `themes/umbrella/payout/transfer-authorized-seal.svg` — ✅ present
- `themes/umbrella/ui/containment-division-badge.svg` — ✅ present
- `themes/umbrella/ui/facility-schematic.svg` — ✅ present
- `themes/umbrella/ui/specimen-vial.svg` — ✅ present
- `themes/umbrella/ui/surveillance-terminal.svg` — ✅ present
- `themes/umbrella/ui/umbrella-containment-emblem.svg` — ✅ present

## Workflow inventory

- `.github/workflows/actions-security-audit.yml` — review as possible temporary workflow
- `.github/workflows/apply-development-package.yml`
- `.github/workflows/asset-health-monitor.yml` — review as possible temporary workflow
- `.github/workflows/branch-cleanup-audit.yml` — review as possible temporary workflow
- `.github/workflows/code-integrity-audit.yml` — review as possible temporary workflow
- `.github/workflows/discord-commit-notifications.yml`
- `.github/workflows/discord-development-status.yml` — review as possible temporary workflow
- `.github/workflows/documentation-drift-check.yml` — review as possible temporary workflow
- `.github/workflows/full-userscript-audit.yml` — review as possible temporary workflow
- `.github/workflows/github-pages.yml` — review as possible temporary workflow
- `.github/workflows/greasyfork-release-monitor.yml`
- `.github/workflows/import-canonical-userscript.yml`
- `.github/workflows/owner-release-command.yml`
- `.github/workflows/pages-production-monitor.yml` — review as possible temporary workflow
- `.github/workflows/performance-regression-check.yml` — review as possible temporary workflow
- `.github/workflows/prepare-release-rollback.yml` — review as possible temporary workflow
- `.github/workflows/reconcile-release-announcement-state.yml`
- `.github/workflows/release-planning.yml` — review as possible temporary workflow
- `.github/workflows/release-readiness-check.yml` — review as possible temporary workflow
- `.github/workflows/release-recovery-validation.yml`
- `.github/workflows/release-recovery.yml`
- `.github/workflows/release-toolkit-dry-run.yml` — review as possible temporary workflow
- `.github/workflows/release-toolkit.yml` — review as possible temporary workflow
- `.github/workflows/repository-audit.yml` — review as possible temporary workflow
- `.github/workflows/sync-repository-labels.yml`
- `.github/workflows/update-release-dashboard.yml`
- `.github/workflows/userscript-structural-audit.yml` — review as possible temporary workflow
- `.github/workflows/validate-issue-intake.yml`
- `.github/workflows/validate-userscript.yml` — review as possible temporary workflow

## Referenced GitHub Actions secrets

- `DISCORD_COMMITS_WEBHOOK`
- `DISCORD_RELEASE_WEBHOOK`
- `MIGRATION_REPO_TOKEN`

## Safety findings

- Every discovered raw repository path referenced by the current script exists in the repository.
- Existing public media paths remain protected and should not be reorganised in place.
- New source, distribution and backup directories should be added alongside existing assets.

## Next controlled steps

1. Review the generated dependency list.
2. Import the current Greasy Fork userscript into a new canonical `src/` path without changing public distribution.
3. Add validation and compare the imported source against the live Greasy Fork copy.
4. Introduce `dist/` only after byte-level validation succeeds.
5. Replace the legacy polling release path only after a complete end-to-end dry run.
