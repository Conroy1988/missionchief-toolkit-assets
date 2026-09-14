# Security Policy

Security-sensitive reports should not be posted publicly when they include exploitable details, credentials, webhook URLs, private repository information, or a reproducible path that could compromise Toolkit users.

## Supported version

Only the current Chrome Web Store extension release is actively supported. The Tampermonkey/userscript edition is unsupported. Older releases remain available for recovery and audit purposes, but security fixes are applied to the current release line.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature when available. Include:

- affected Toolkit version;
- affected browser, extension version and installation source;
- concise impact assessment;
- reproducible steps or a minimal proof of concept;
- whether credentials, private URLs, or user data are involved;
- any proposed mitigation.

Do not include live credentials, webhook URLs, access tokens, private repository contents, or personal data in a public issue.

## Response process

A credible report will be triaged against the current extension source and packaged behaviour. Confirmed issues may trigger a guarded hotfix, release recovery procedure, asset revocation, secret rotation, or an emergency rollback candidate. Public disclosure will follow remediation where practical.

## Release integrity

Install the extension from the [Chrome Web Store](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc). Source and test packages do not imply Store approval. Historical userscript releases and hashes remain available for provenance. All executable extension code is bundled locally.
