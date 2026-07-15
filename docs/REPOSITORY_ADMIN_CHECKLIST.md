# Repository Administration Checklist

This checklist covers GitHub settings that cannot be completed through normal repository commits.

## Already configured or verified

- [x] Repository is public
- [x] GitHub Pages uses GitHub Actions
- [x] Pages deployment succeeds
- [x] `main` deletion protection enabled
- [x] `main` force-push protection enabled
- [x] Structured issue forms active
- [x] Managed repository labels synchronised

## Manual account-level actions

### Community

- [ ] Enable GitHub Discussions
- [ ] Create recommended Discussion categories
- [ ] Create and publish the MissionChief Toolkit Roadmap Project

### Repository presentation

- [ ] Upload a repository social-preview image
- [ ] Review repository description and topic tags
- [ ] Decide whether to configure a custom Pages domain
- [ ] Configure DNS and Pages HTTPS enforcement if a custom domain is chosen

### Branch and access administration

- [ ] Review obsolete merged branches and delete confirmed-safe candidates
- [ ] Review repository collaborators and installed GitHub Apps
- [ ] Confirm secret access is limited to required workflows
- [ ] Review Dependabot pull requests before merging Action updates

### Future strict protection

- [ ] Complete `docs/BRANCH_PROTECTION_MIGRATION.md`
- [ ] Introduce a narrowly scoped release GitHub App
- [ ] Rehearse normal release and every partial-recovery path
- [ ] Require pull requests and required status checks
- [ ] Require conversation resolution
- [ ] Block direct human pushes to `main`

## Node.js Action warnings

Official GitHub Actions may temporarily emit runtime deprecation warnings while GitHub moves hosted actions between Node.js generations. Current actions are pinned and Dependabot monitors updates. Replace pins only through reviewed Dependabot or maintenance pull requests after the new action commit is verified.
