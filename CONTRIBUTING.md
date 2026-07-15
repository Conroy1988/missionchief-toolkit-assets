# Contributing

The MissionChief Map Command Toolkit is maintained through reviewed, validated changes to the canonical userscript and its release infrastructure.

## Before opening a change

- Search existing issues and pull requests.
- Use the structured issue forms for bugs, performance reports and feature proposals.
- Keep public reports free of credentials, webhook URLs and private repository details.
- Separate unrelated fixes into distinct changes where practical.

## Development expectations

- Preserve the existing Desktop, Tablet and iOS operating modes.
- Preserve all supported themes unless a change explicitly targets them.
- Avoid eager document-start work, broad DOM scans and unbounded observers.
- Do not introduce duplicate interface IDs or shortcut conflicts.
- Keep public asset paths stable or update the asset-health policy in the same change.
- Update user-facing documentation and changelog data when behaviour changes.

## Validation

Pull requests may run userscript validation, code-integrity auditing, performance-regression checks, asset-health checks and documentation-site validation. Do not bypass a failed check without identifying and correcting the underlying cause.

## Releases

Do not manually publish partial release state. Production releases use the reviewed release-readiness and release workflows, which coordinate GitHub Releases, Greasy Fork, the private migration archive, status records and Discord announcements.

## Pull-request content

Describe:

- the problem being solved;
- the affected Toolkit area;
- behaviour before and after;
- desktop, tablet and iOS implications;
- performance implications;
- validation performed;
- whether a public Toolkit version is required.
