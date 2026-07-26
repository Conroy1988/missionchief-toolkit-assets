# Consolidated Pull-Request Gate

Pipeline v5.1 consolidates release-critical pull-request validation into the existing **Validate Canonical Userscript** workflow.

## Four parallel lanes

1. **Runtime** — deterministic contracts, JavaScript syntax and distribution parity.
2. **Integrity** — canonical validation, structural audit, code integrity, static analysis, ESLint and immutable release-candidate packaging.
3. **Performance** — absolute/differential budgets and deep AST performance analysis.
4. **Repository** — workflow/security policy, documentation, Pages, assets, stable manifest, Greasy Fork parity and advisory release planning.

The final **Toolkit Hotfix Gate** job succeeds only when all four lanes succeed.

Legacy workflows retain their manual, scheduled and production triggers, but no longer provision separate pull-request runners. Pipeline v5 validated-tree promotion continues to consume the exact immutable candidate from this workflow.
