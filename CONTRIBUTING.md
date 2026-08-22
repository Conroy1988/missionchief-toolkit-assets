# Contributing

The MissionChief Map Command Toolkit is maintained through reviewed, validated changes to the canonical userscript and its release infrastructure.

## Before opening a change

- Search existing issues and pull requests.
- Use the structured issue forms for bugs, performance reports and feature proposals.
- Keep public reports free of credentials, webhook URLs and private repository details.
- Separate unrelated fixes into distinct changes where practical.

## Roadmap and issue flow

- Use **Discussions → Feature ideas** for early concepts that still need community or design exploration.
- Use **GitHub Issues** for confirmed bugs, improvements and actionable technical specifications.
- Apply the `roadmap` label only to planned product or engineering work that belongs in the public development queue.
- Keep labels orthogonal: roadmap labels show planned inclusion, type labels describe the work, and priority labels express urgency.
- Do not duplicate scheduling state in a separate roadmap document or Project.
- Link implementation pull requests to the relevant Issue so merged work automatically becomes part of the completed development record.

## Development expectations

- Preserve the existing Desktop, Tablet and iOS operating modes.
- Preserve all supported themes unless a change explicitly targets them.
- Avoid eager document-start work, broad DOM scans and unbounded observers.
- Do not introduce duplicate interface IDs or shortcut conflicts.
- Keep public asset paths stable or update the asset-health policy in the same change.
- Update user-facing documentation and changelog data when behaviour changes.

## Routine delivery path

Contained userscript changes should use the fastest safe route:

1. Create one owner-authored `feature/`, `fix/` or `chore/` branch from current `main`.
2. Complete the source, generated distribution, changelog and focused contract in that branch.
3. Generate the single candidate fingerprint and run the CI-equivalent local gate:

   ```bash
   ./toolkit promote
   ```

4. Open one pull request.
5. Allow the single-runner Toolkit Hotfix Gate to complete its path-aware checks.
6. Merge the exact reviewed head and use the permanent guarded release command when a public version is required.

Do not create diagnostic pull requests or test-only commits when the required code and fixtures can be prepared and verified before the pull request is opened.

## Reviewed development packages

The owner-authorised development-package workflow remains available for large generated transformations, exact-source rewrites and changes that are safer to apply inside the repository runner. It is not the default route for small, contained edits.

## Validation

Pull requests use one path-aware Toolkit Hotfix Gate runner. Local promotion and CI invoke the same version-controlled candidate stages. Fingerprint, documentation, syntax and lightweight performance failures are evaluated before distribution generation, dependency installation and runtime contracts, then the immutable release candidate is uploaded from that same exact checkout. Exhaustive static, ESLint, deep-performance and repository-wide audits remain scheduled or manually dispatched instead of multiplying every pull request into parallel jobs. Do not bypass a failed check without identifying and correcting the underlying cause.

## Releases

Do not manually publish partial release state. Production releases use the reviewed release-readiness and release workflows, which coordinate GitHub Releases, TKB Website distribution, the private migration archive, authoritative `release-state` records and Discord announcements.

## Pull-request content

Describe:

- the problem being solved;
- the affected Toolkit area;
- behaviour before and after;
- desktop, tablet and iOS implications;
- performance implications;
- validation performed;
- whether a public Toolkit version is required.
