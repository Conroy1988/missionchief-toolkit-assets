# MissionChief Map Command Toolkit Roadmap

This roadmap separates verified infrastructure, active Toolkit development and repository-administration work that requires GitHub account controls.

## Completed foundation

- Canonical userscript source and byte-identical distribution generation
- Release Readiness and production publication workflows
- GitHub Release, Greasy Fork, private migration backup and Discord coordination
- Duplicate-announcement protection and partial release recovery
- Reviewed rollback-candidate preparation
- Performance regression budgets
- Code-integrity and userscript-structure auditing
- Public asset-health monitoring
- Structured issue forms and managed labels
- GitHub Pages documentation site
- GitHub Actions supply-chain pinning, permission auditing and Dependabot
- Documentation contract and live Pages monitoring
- Read-only release planning

## Active Toolkit development

### Smart map presentation

- Continue reducing bookmark footprint without damaging theme identity.
- Extend intelligent label shortening and user overrides where real-world place names expose gaps.
- Preserve Desktop, Tablet and iOS behaviour.

### Operational intelligence

- Continue Mission Age Watch, Critical View, Mission Inspector and transport-state refinement.
- Expand live selector resilience when MissionChief changes markup.
- Preserve deferred startup and on-demand interface construction.

### Performance

- Measure startup and first-interaction costs on large accounts.
- Reduce unnecessary observers, selectors and eager controls.
- Keep CI budgets calibrated to real regressions rather than normal feature growth.

## Documentation and community

- Capture real Desktop, Tablet and iOS screenshots.
- Record short demonstrations for major workflows and themes.
- Enable GitHub Discussions and create a public GitHub Project when repository administration permits.
- Add media to the generated Pages gallery using the documented capture manifest.

## Repository architecture

- Move generated release state away from protected source where practical.
- Introduce a narrowly scoped GitHub App identity for release automation.
- Rehearse the complete release and recovery pipeline under that identity.
- Enable strict PR-only protection only after the rehearsal passes.

## Optional administration

- Configure a repository social-preview image.
- Consider a custom documentation domain.
- Delete obsolete merged branches after reviewing the generated branch-cleanup candidates.
- Review Dependabot Action updates and upstream Node.js runtime migrations.

## Decision rule

Public Toolkit releases remain separate from repository-only infrastructure work. A repository improvement does not increase the Toolkit version unless the canonical userscript or user-facing distribution changes.
