# Repository and dependency audit

> Generated automatically. This audit does not rename, move or delete files.

## Summary

- Repository files: **122**
- Media files: **28**
- GitHub Actions workflows: **19**
- Greasy Fork version: **4.11.2**
- Repository URLs referenced by current script/repository: **25**
- Missing referenced paths: **0**
- Possible one-shot workflows: **0**
- Duplicate media groups: **1**

## Current userscript source

Greasy Fork was read successfully at version **4.11.2**.
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

- `.github/workflows/asset-health-monitor.yml`
- `.github/workflows/code-integrity-audit.yml`
- `.github/workflows/discord-commit-notifications.yml`
- `.github/workflows/discord-development-status.yml`
- `.github/workflows/greasyfork-release-monitor.yml`
- `.github/workflows/import-canonical-userscript.yml`
- `.github/workflows/performance-regression-check.yml`
- `.github/workflows/prepare-release-rollback.yml`
- `.github/workflows/reconcile-release-announcement-state.yml`
- `.github/workflows/release-readiness-check.yml`
- `.github/workflows/release-recovery-validation.yml`
- `.github/workflows/release-recovery.yml`
- `.github/workflows/release-toolkit-dry-run.yml`
- `.github/workflows/release-toolkit.yml`
- `.github/workflows/repository-audit.yml`
- `.github/workflows/sync-repository-labels.yml`
- `.github/workflows/update-release-dashboard.yml`
- `.github/workflows/validate-issue-intake.yml`
- `.github/workflows/validate-userscript.yml`

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
