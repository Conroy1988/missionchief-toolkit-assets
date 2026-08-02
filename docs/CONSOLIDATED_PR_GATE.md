# Consolidated Pull-Request Gate

Pipeline v5.2 consolidates release-critical pull-request validation into the existing **Validate Canonical Userscript** workflow and selects blocking work from the exact changed paths.

## Four parallel lanes

1. **Runtime** — deterministic contracts, JavaScript syntax and distribution parity.
2. **Integrity** — canonical validation, structural audit, code integrity, static analysis, ESLint and immutable release-candidate packaging.
3. **Performance** — absolute/differential budgets and deep AST performance analysis.
4. **Repository** — workflow/security policy, documentation, Pages, assets, the stable TKB manifest and advisory release planning.

The final **Toolkit Hotfix Gate** job succeeds only when every classifier-required lane succeeds. Lanes that are explicitly unnecessary are skipped without leaving the required aggregate check pending.

Exhaustive static and ESLint analysis, deep AST analysis and external stable-channel parity are no longer unconditional on the pull-request critical path. Unknown paths fail closed by requiring every lane, exhaustive audits and candidate generation.

Legacy workflows retain their manual, scheduled and production triggers, but no longer provision separate pull-request runners. Pipeline v5 validated-tree promotion continues to consume the exact immutable candidate from product-changing pull requests, while non-product merges stop before artifact lookup or fallback validation.
