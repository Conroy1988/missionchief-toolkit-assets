# Toolkit code-integrity auditing

The code-integrity audit protects the MissionChief Map Command Toolkit against structural defects that can pass JavaScript syntax validation but still break the interface, release pipeline or public installation.

## Checks

The audit validates:

- userscript metadata cardinality and required values;
- MissionChief UK match/include coverage;
- newly introduced duplicate static DOM IDs;
- newly introduced keyboard shortcut collisions;
- malformed fully static `querySelector`, `querySelectorAll`, `matches` and `closest` selectors;
- unresolved merge-conflict markers in tracked text files;
- high-confidence committed secrets such as Discord webhooks, GitHub tokens, cloud keys and private keys;
- insecure runtime URLs and GitHub blob-page media URLs;
- same-repository raw asset URLs against committed files;
- the existing static public-asset-health contract.

## Baseline comparison

Duplicate IDs and shortcut collisions are compared with a baseline userscript:

- pull requests use their target branch;
- pushes to `main` use the previous commit;
- manual runs use the latest versioned release tag where available.

Existing legacy duplicates remain visible in the report but do not fail unchanged code. A new duplicate value or an increased occurrence count fails the audit. This prevents new collisions without forcing unrelated development to rewrite the complete legacy interface.

## Conservative parsing

The auditor evaluates only high-confidence static constructs:

- literal `id="..."`, `.id = "..."` and `setAttribute("id", "...")` assignments;
- literal key comparisons inside detected `keydown` handlers and explicit `data-hotkey`/`data-shortcut` attributes;
- selector calls whose complete first argument is one static string.

Dynamically assembled selectors and IDs are skipped rather than guessed. Existing performance and asset-health checks continue to cover their own domains.

## Policy changes

`.github/code-integrity-policy.json` controls metadata expectations, repository text-file coverage, intentional duplicate allowlists and runtime URL rules.

Do not add an allowlist entry merely to make CI green. First verify that the duplicate ID or shortcut is intentional, cannot create simultaneous conflicting interface elements, and is documented in the pull request.

## Diagnostics

Every workflow run uploads JSON and Markdown reports for 30 days. The reports include:

- current interface-ID inventory;
- current shortcut-conflict inventory;
- validated selector count;
- scanned repository text-file count;
- runtime URL and same-repository asset statistics;
- exact failure locations where available.
