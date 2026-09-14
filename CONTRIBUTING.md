# Contributing

Develop the **Chrome extension**. The userscript distribution is retired and retained for historical reference and migration delivery.

## Before changing code

Verify the current `main` branch and existing work. Use a feature branch and a pull request; respect branch protections, reviews and required checks. Keep unrelated work separate. Include the problem, resulting behaviour, tests and material limitations in the PR.

## Extension development

Follow [extension/README.md](extension/README.md) for the baseline, maintained modules and build commands. Test changes to game actions against meaningful native-response fixtures, including failures after a successful action. Never count a test as proof of a live game purchase.

Preserve account ownership checks, explicit confirmation, Credit-only purchase selection, saved progress and uncertain-request recovery. Avoid duplicate purchases, unbounded scans, unnecessary catalogue downloads and eager UI work. Keep desktop and touch layouts usable. Do not add remote executable code.

## Documentation and graphics

The Chrome Web Store link is the installation authority. Distinguish submitted, approved and test versions. New feature claims must match the packaged extension. Artwork must be clearly distinguished from actual screenshots; do not use fabricated game screenshots or private account data. Credit Conroy1988 as the sole Toolkit developer. Do not attribute Toolkit development or assistance to MartyBlyth. Preserve historical licence notices.

## Legacy migration

See [legacy/README.md](legacy/README.md). Existing Tampermonkey update URLs must remain reachable to deliver the final notice. A prepared migration package is not a deployment. Do not run an old userscript release pipeline as if it publishes a Chrome extension.

Historical source and release workflow documents describe the retired distribution. They are retained for provenance, and are not the current installation instructions.

## Security

Never commit credentials or real webhook URLs. Review [SECURITY.md](SECURITY.md) and redact reports. Use the issue templates for reproducible bugs, performance reports and feature requests.
