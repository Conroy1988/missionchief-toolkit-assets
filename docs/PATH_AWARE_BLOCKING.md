# Path-aware blocking rules

Pipeline v5.2 keeps one required **Toolkit Hotfix Gate**, but provisions only the validation work justified by the pull request's exact changed paths.

## Blocking model

- **Product changes** run Runtime, Integrity and Performance lanes and produce the immutable exact-tree release candidate.
- **Runtime-contract changes** run Runtime plus Repository validation.
- **Integrity-tooling changes** run Integrity plus Repository validation. Exhaustive static and ESLint work runs only when its own policy or tooling changes, or during an explicit full dispatch.
- **Performance-tooling changes** run Performance plus Repository validation. The deep AST audit runs only when its own tooling changes, or during an explicit full dispatch.
- **Documentation-only changes** run the relevant documentation and Pages contracts in the Repository lane and do not create or promote a userscript candidate.
- **Asset and theme changes** run asset-health checks without pretending that an unchanged userscript version is a new release candidate.
- **Repository, release and workflow changes** activate their relevant policy checks.
- **Unknown paths fail closed** by requiring every lane, exhaustive audits and a release candidate until the policy explicitly classifies them.

The aggregate gate accepts a skipped lane only when the classifier explicitly marked that lane as unnecessary. A required lane must conclude successfully.

## Release promotion

The automatic release controller reuses the same policy against the merged pull-request diff before looking for validation artifacts. If no release-critical product path changed, promotion stops successfully without dispatching the guarded full-main fallback. Product changes still require the exact successful pull-request candidate and exact-tree match used by Pipeline v5.

## Exhaustive and external audits

Full static and ESLint audits plus deep AST analysis remain available through explicit full dispatches and their retained dedicated workflows. Retired external distribution checks are not part of pull-request validation or release publication.
