# Security Policy

Security-sensitive reports should not be posted publicly when they include exploitable details, credentials, webhook URLs, private repository information, or a reproducible path that could compromise Toolkit users.

## Supported version

Only the latest verified MissionChief Map Command Toolkit release is actively supported. Older releases remain available for recovery and audit purposes, but security fixes are applied to the current release line.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature when available. Include:

- affected Toolkit version;
- affected browser and userscript manager;
- concise impact assessment;
- reproducible steps or a minimal proof of concept;
- whether credentials, private URLs, or user data are involved;
- any proposed mitigation.

Do not include live credentials, webhook URLs, access tokens, private repository contents, or personal data in a public issue.

## Response process

A credible report will be triaged against the current canonical userscript and release pipeline. Confirmed issues may trigger a guarded hotfix, release recovery procedure, asset revocation, secret rotation, or an emergency rollback candidate. Public disclosure will follow remediation where practical.

## Release integrity

Official releases are distributed through the repository's verified GitHub Release, Greasy Fork publication, private migration archive, manifest and SHA-256 records. Do not trust userscript copies from unrelated mirrors.
