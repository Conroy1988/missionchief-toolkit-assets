# Path-aware blocking rules

Pipeline v5.3 keeps one required **Toolkit Hotfix Gate** and one GitHub runner, executing only the validation work justified by the pull request's exact changed paths.

## Blocking model

- **Product changes** run canonical Integrity generation, Runtime contracts and the lightweight Performance budget sequentially, then produce the immutable exact-tree release candidate.
- **Runtime-contract changes** run the deterministic Runtime checks on the same runner.
- **Integrity-tooling changes** run canonical Integrity checks on the same runner. Exhaustive static and ESLint work remains in the dedicated scheduled/manual audit.
- **Performance-tooling changes** run the lightweight Performance budget on the same runner. Deep AST analysis remains in the dedicated scheduled/manual audit.
- **Documentation-only changes** do not create or promote a userscript candidate.
- **Asset and theme changes** run asset-health checks without pretending that an unchanged userscript version is a new release candidate.
- **Local development and canary-tooling changes** run the Dev Lab and canary integrity contracts without producing or promoting a stable userscript candidate. Product changes also run the same three-viewport canonical-source mount as an independent final UI proof.
- **Repository, release and workflow changes** activate their relevant policy checks.
- **Unknown paths fail closed** by requiring every lane, exhaustive audits and a release candidate until the policy explicitly classifies them.

The gate omits a check only when the classifier explicitly marks it unnecessary. Every selected check must conclude successfully before its single job can pass.

## Release promotion

The automatic release controller reuses the same policy against the merged pull-request diff before looking for validation artifacts. If no release-critical product path changed, promotion stops successfully without dispatching the guarded full-main fallback. Product changes still require the exact successful pull-request candidate and exact-tree match used by Pipeline v5.

## Exhaustive and external audits

Full static and ESLint audits plus deep AST and repository-wide analysis remain available through scheduled/manual dedicated workflows. They do not fan out ordinary pull requests. Retired external distribution checks are not part of pull-request validation or release publication.
